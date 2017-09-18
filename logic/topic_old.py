#coding=utf-8
import webdriver
import db
import utils
import logging
import ConfigParser
import time
import task_mgr
import crawl_rule
import sys
import traceback
import os
import cPickle
import threading
import urllib2
import gc
reload(sys)
sys.setdefaultencoding('utf8')

def visit_page(topic_dict, db_conn, expend = False, expend_topic_dict = None):
	num_page = len(topic_dict)
	cur_num = 0
	failed_page = 0
	thread_name = threading.current_thread().getName()
	start_time = time.time()
	for key, val in topic_dict.iteritems():
		cur_num += 1
		url = 'https://www.zhihu.com/topic/' + key
		topic_name = None
		topic_focus = None
		try:
			soup = utils.get_soup_request(url)
			topic_name = crawl_rule.topic_name(soup)
			topic_focus = crawl_rule.topic_focus(soup, key)

			if topic_name is None or topic_focus is None:
				raise Exception('linkid: %s: topic name or topic is None!'% key)

			sql_str = 'INSERT IGNORE INTO TOPIC (LINK_ID, NAME, FOCUS, LAST_VISIT, ADD_TIME) VALUES (%s, %s, %s, %s, %s)'
			db_conn.execute(sql_str, [(key, topic_name, topic_focus, val['last_visit'], val['add_time'])])
	
			if expend == True:
				topic_links_l2 = utils.get_links(soup, crawl_rule.l2_topics)
				utils.add_new_topics(topic_links_l2, expend_topic_dict)
			soup.decompose()
			gc.collect()
		except Exception, e:
			traceback.print_exc()
			logging.fatal(e)
			failed_page += 1
#			utils.save_page(key, soup.text)
		
		#debug
		page_level = 'L1'
		if expend == False:
			page_level = 'L2'
		cur_time = time.time()
		logging.info('%s: visit %s page name:%s focus:%s; visit:%d; failed:%d;total:%d; speed: %.2f page/min  ', thread_name,  page_level, topic_name, topic_focus, cur_num, failed_page, num_page, cur_num/(cur_time-start_time)*60)

	logging.info('visit_page finished %d/%d failed', failed_page, num_page)

class TopicSpider:
	def __init__(self):
		self.wd = webdriver.WebDriver()
		self.db_conn = db.DBConnection()
		self.rst = None

	def login(self):
		self.wd.login()

	def get_l1_topic(self, top_topics):
		self.rst = {}
		for top_topic_link in top_topics:
			if top_topic_link[0] == '#':
				top_topic_link = 'https://www.zhihu.com/topics' + top_topic_link

			logging.info('visit page: %s', top_topic_link)
			soup = utils.get_soup(self.wd, top_topic_link, scroll_end = True)
				
			#获取子话题链接
			topic_links = utils.get_links(soup, crawl_rule.sub_topics)
			utils.add_new_topics(topic_links, self.rst)

			logging.info('current num of topics: %d', len(self.rst))

	def visit_topic_page(self, l1_topics):
		#访问所有l1 topic并添加 l2 topic
		logging.info('visit L1 topics; num of L1 topics: %d', len(l1_topics))
		l2_topics = {}
		visit_page(l1_topics, self.db_conn, True, l2_topics)

		#访问所有l2 topic 
		logging.info('visit L2 topics; num of L2 topics: %d', len(l2_topics))
		visit_page(l2_topics, self.db_conn)

def get_l1_topic(tm, spider_list, write_path):
	#获取顶层话题	
	soup = utils.get_soup(spider_list[0].wd, 'https://www.zhihu.com/topics')	
	top_topic_links = utils.get_links(soup, crawl_rule.top_topics)

	#获取L1 topic
	tm.set_task(task_name = 'get_l1_topic', data = top_topic_links)
	tm.run()
	l1_topics = tm.get_result()
	f = open(write_path, 'wb')
	cPickle.dump(l1_topics, f)
	f.close()

def get_unvisited_topics(db_conn, l1_topics):
	sql_str = 'SELECT LINK_ID from TOPIC'
	db_conn.execute(sql_str, [])
	results = db_conn.fetch_results()
	total_num = len(l1_topics)
	for row in results:
		linkid = str(row[0])
		if l1_topics.has_key(linkid):
			del l1_topics[linkid]

	logging.info('total l1 topics: %d, unvisited l1 topics: %d', total_num, len(l1_topics))

def run():
	cf = ConfigParser.ConfigParser()
	cf.read('config.ini')
	utils.init_logger(cf.get('log', 'topic_path'))
	spider_list = []
	num_thread = int(cf.get('general', 'num_thread'))
	for i in xrange(num_thread):
		spider_list.append(TopicSpider())
	tm = task_mgr.TaskManager()
	tm.add_workers(spider_list)

#	获取topic不需要登录
#	for spider in spider_list:
#		spider.login()

#	print 'waiting for user operation'	
#	time.sleep(20)
	
	#查看是否已有h1 topic的dump，如果没有再生成
	l1_topics = None
	l1_topic_path = cf.get('topic', 'l1_topic_path')
	if os.path.exists(l1_topic_path) == True:
		logging.info('load L1 topic from file')
		f = open(l1_topic_path, 'rb')
		l1_topics = cPickle.load(f)
		f.close()
	else:
		l1_topics = get_l1_topic(tm, spider_list, l1_topic_path)
	
	#从数据库取出没有被访问过的页面,减少待爬取的链接数量
	get_unvisited_topics(spider_list[0].db_conn, l1_topics)

	#获取L2 topic 并访问所有topic页面
	tm.set_task(task_name = 'visit_topic_page', data = l1_topics)
	tm.run()	
	logging.info('finished')
		
if __name__ == '__main__':
	run()
