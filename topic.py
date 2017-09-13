#coding=utf-8
import webdriver
#import db
import utils
import logging
import ConfigParser
import re
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
from bs4 import BeautifulSoup

reload(sys)
sys.setdefaultencoding('utf8')

def gen_topic_sql_params(param_list, topic_dict):
	for key, val in topic_dict.iteritems():
		if val['name'] is not None:
			param_list.append((key, val['name'], val['focus'], val['last_visit'], val['add_time']))
#		else:
#			logging.fatal('topic %s does not have name')

def visit_page(topic_dict, expend = False, expend_topic_dict = None):
	num_page = len(topic_dict)
	cur_num = 0
	failed_page = 0
	thread_name = threading.current_thread().getName()
	start_time = time.time()
	for key, val in topic_dict.iteritems():
		cur_num += 1
		url = 'https://www.zhihu.com/topic/' + key

		try:
			soup = utils.get_soup_request(url)
			val['name'] = crawl_rule.topic_name(soup)
			val['focus'] = crawl_rule.topic_focus(soup, key)
			if expend == True:
				topic_links_l2 = utils.get_links(soup, crawl_rule.l2_topics)
				utils.add_new_topics(topic_links_l2, expend_topic_dict)
			soup.decompose()
			gc.collect()
		except Exception, e:
			traceback.print_exc()
			logging.fatal(e)
			logging.fatal('topic page %s does not have name or focus', key)
			failed_page += 1
#			utils.save_page(key, soup.text)
		
		#debug
		page_level = 'L1'
		if expend == False:
			page_level = 'L2'
		cur_time = time.time()
		logging.info('%s: visit %s page name:%s focus:%s; visit:%d; failed:%d;total:%d; speed: %.2f page/min  ', thread_name,  page_level, val['name'], val['focus'], cur_num, failed_page, num_page, cur_num/(cur_time-start_time)*60)

	logging.info('visit_page finished %d/%d failed', failed_page, num_page)

class TopicSpider:
	def __init__(self):
		self.wd = webdriver.WebDriver()
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
		visit_page(l1_topics, True, l2_topics)

		#访问所有l2 topic 
		logging.info('visit L2 topics; num of L2 topics: %d', len(l2_topics))
		visit_page(l2_topics)

		self.rst = {}
		self.rst.update(l1_topics)
		self.rst.update(l2_topics)

	def run(self):
		self.cur_task()

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

def run():
	utils.init_logger()
	cf = ConfigParser.ConfigParser()
	cf.read('config.ini')
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
	print len(l1_topics)
	#获取L2 topic 并访问所有topic页面
	tm.set_task(task_name = 'visit_topic_page', data = l1_topics)
	tm.run()
	all_topics = tm.get_result()

	param_list = []
	gen_topic_sql_params(param_list, all_topics)
		
	logging.info('insert data to db')
	db_conn = db.DBConnection()
	sql_str = 'INSERT IGNORE INTO TOPIC (LINK_ID, NAME, FOCUS, LAST_VISIT, ADD_TIME) VALUES (%s, %s, %s, %s, %s)'
	db_conn.execute(sql_str, param_list)
	db_conn.close()	
	logging.info('finished')
		
if __name__ == '__main__':
	run()
