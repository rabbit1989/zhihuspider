#coding=utf-8
import sys
import common.db as db
import MySQLdb
import logic.logic_base as logic_base
import utils
import logging
import ConfigParser
import time
import crawl_rule
import traceback
import os
import cPickle
import threading
import gc
import common.utils
import re
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

failed_topics = {}

def visit_page(topics):
	output = {'org':[], 'expend':[]}
	topic_failed = []
	linkid_pattern = re.compile('/[0-9]+')
	for ele in topics:
		topic_id = ele[0]
		val = ele[1]
		try:
			cur_time = common.utils.get_sql_time()
			url = 'https://www.zhihu.com/topic/' + topic_id
			resp, html_text = common.utils.get_response(url)
			if resp == None or html_text == None:
				raise Exception('urllib2 error')

			actual_url = resp.geturl()
			actual_linkid = re.search(linkid_pattern, actual_url).group()[1:]

			soup = BeautifulSoup(html_text, 'lxml')
			topic_name = crawl_rule.topic_name(soup)
			topic_focus = crawl_rule.topic_focus(soup, topic_id)
			if topic_name is None or topic_focus is None:
				raise Exception('linkid: %s: topic name or topic is None!'% topic_id)
			output['org'].append((actual_linkid, {'name':topic_name, 'focus':topic_focus, 'last_visit':cur_time, 'add_time':cur_time}))	
			logging.info('visit page name:%s focus:%s; ', topic_name, topic_focus)
			if val['expend'] == True:
				topic_links_l2 = utils.get_links(soup, crawl_rule.l2_topics)
				logging.info('get %d expend pages', len(topic_links_l2))
				utils.add_new_topics(topic_links_l2, output['expend'])			
			soup.decompose()
			gc.collect()
		except Exception, e:
			logging.fatal(e)
			if not failed_topics.has_key(topic_id):
				failed_topics[topic_id] = 0
			failed_topics[topic_id] += 1
			if failed_topics[topic_id] < 5:
				topic_failed.append(ele)
			else:
				logging.info('topic %s failed too many times, abandened', topic_id)

	return topic_failed, output

class topic_logic(logic_base.logic_base):
	def __init__(self):
		logic_base.logic_base.__init__(self)
		work_dir = os.path.dirname(os.path.abspath(__file__))
		config_file_path = os.path.join(work_dir,'config.ini')
		self.cf = ConfigParser.ConfigParser()
		self.cf.read(config_file_path)
		self.db_conn = db.DBConnection(self.cf)
		self.topics = {}
		self.num_visited_pages = 0
		self.num_received_results = 0
		self.start_time = -1
		#只在crawl_master端使用
		self.unique_topics = {}

	def assign_works(self, ):
		'''
			called on crawl master
		'''
		logging.info('num of visited page: %d', self.num_visited_pages)
		if self.start_time < 0:
			self.start_time = time.time()
		data = None
		if len(self.topics) > self.num_visited_pages:
			data = self.topics[self.num_visited_pages:self.num_visited_pages+10]
			self.num_visited_pages += 10
		return data

	def receive_work_result(self, result):
		'''
			called on crawl master
		'''
		logging.info('num of result: %d', len(result['org']))
		self.num_received_results += len(result['org'])
		cur_time = time.time()
		for ele in result['org']:
			try:
				sql_str = 'INSERT IGNORE INTO topic (link_id, name, focus, last_visit, add_time) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE focus = %s, last_visit = %s'
				self.db_conn.execute(sql_str, [(ele[0], ele[1]['name'], ele[1]['focus'], ele[1]['last_visit'], ele[1]['add_time'], ele[1]['focus'], ele[1]['last_visit'])])
			except MySQLdb.Error, e:
				self.db_conn.process_exception(e)

		for ele in result['expend']:
			if not self.unique_topics.has_key(ele[0]):
				logging.info('expend topic %s is new, add to task list', ele[0])
				self.unique_topics[ele[0]] = True
				self.topics.append(ele)
			else:
				logging.warn('expend topic %s has been processed, skipped', ele[0])
		
		logging.info('process speed so far: %d pages/min; %d pages to be processed', self.num_received_results/(cur_time-self.start_time)*60, len(self.topics)-self.num_visited_pages)

	def on_assign_works(self, _input):
		'''
			called on crawl slave
		'''
		logging.info('num of input: %d', len(_input))
		input_unfinished, output = visit_page(_input)
		logging.info('%d/%d success', len(output['org']), len(_input))
		return input_unfinished, output, 

	def prepare_work(self, ):
		'''
			called on crawl master
		'''
		logging.info('topic spider: prepare work')
		#查看是否已有h1 topic的dump，如果没有再生成
		l1_topic_path = self.cf.get('topic', 'l1_topic_path')
		if os.path.exists(l1_topic_path) == True:
			logging.info('load L1 topic from file')
			f = open(l1_topic_path, 'rb')
			self.topics = cPickle.load(f)
			f.close()
		else:
			raise Exception('l1 topics does not exist')
		
		#给每一个topic加上expend标签，expend为True说明需要在话题页爬取其他话题的链接
		#初始化unique topic set
		for key, val in self.topics.iteritems():
			val['expend'] = True
			self.unique_topics[key] = True

		self.topics = [(key, val) for key, val in self.topics.iteritems()]

if __name__ == '__main__':
	common.utils.init_logger('log/test_topic_log')
	spider = topic_logic()
	spider.prepare_work()
	for i in xrange(10):
		data = spider.assign_works()
		status, res = spider.on_assign_works(data)
		spider.receive_work_result(res)