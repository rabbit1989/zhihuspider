#coding=utf-8
import db
import utils
import logging
import ConfigParser
import time
import crawl_rule
import sys
import traceback
import os
import cPickle
import threading
import gc
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

def visit_page(topics):
	output = []
	topic_failed = []
	for ele in topics:
		topic_id = ele[0]
		url = 'https://www.zhihu.com/topic/' + topic_id
		topic_name = None
		topic_focus = None
		cur_time = utils.get_sql_time()
		try:
			resp = utils.get_response(url)
			if resp.getcode() != 200:
				raise Exception('response code is abnormal')
			soup = BeautifulSoup(resp.read(), 'lxml')
			topic_name = crawl_rule.topic_name(soup)
			topic_focus = crawl_rule.topic_focus(soup, topic_id)
			if topic_name is None or topic_focus is None:
				raise Exception('linkid: %s: topic name or topic is None!'% topic_id)
			output.append((topic_id, {'name':topic_name, 'focus':topic_focus, 'last_visit':cur_time, 'add_time':cur_time}))	
			soup.decompose()
			gc.collect()
			logging.info('visit page name:%s focus:%s; ', topic_name, topic_focus)
		except Exception, e:
#			traceback.print_exc()
			logging.fatal(e)
			topic_failed.append(ele)
	
	return topic_failed, output

class TopicSpider:
	def __init__(self):
		self.db_conn = db.DBConnection()
		self.l1_topics = {}
		self.num_visited_pages = 0
		self.num_received_results = 0
		self.start_time = -1

	def assign_works(self, ):
		'''
			called on crawl master
		'''
		logging.info('num of visited page: %d', self.num_visited_pages)
		if self.start_time < 0:
			self.start_time = time.time()
		if len(self.l1_topics) <= self.num_visited_pages:
			return None
			
		data = self.l1_topics[self.num_visited_pages:self.num_visited_pages+10]
		self.num_visited_pages += 10
		return data

	def receive_work_result(self, result):
		'''
			called on crawl master
		'''
		logging.info('num of result: %d', len(result))
		self.num_received_results += len(result)
		cur_time = time.time()
		for ele in result:
			try:
				sql_str = 'INSERT IGNORE INTO TOPIC (LINK_ID, NAME, FOCUS, LAST_VISIT, ADD_TIME) VALUES (%s, %s, %s, %s, %s)'
				self.db_conn.execute(sql_str, [(ele[0], ele[1]['name'], ele[1]['focus'], ele[1]['last_visit'], ele[1]['add_time'])])
			except Exception, e:
				traceback.print_exc()
				logging.fatal(e)
		logging.info('process speed so far: %d pages/min', self.num_received_results / (cur_time-self.start_time)*60)


	def on_assign_works(self, _input):
		'''
			called on crawl slave
		'''
		logging.info('num of input: %d', len(_input))
		input_unfinished, output = visit_page(_input)
		logging.info('%d/%d success', len(output), len(_input))
		return input_unfinished, output

	def prepare_work(self, ):
		logging.info('topic spider: prepare work')
		cf = ConfigParser.ConfigParser()
		cf.read('config.ini')
		#查看是否已有h1 topic的dump，如果没有再生成
		l1_topic_path = cf.get('topic', 'l1_topic_path')
		if os.path.exists(l1_topic_path) == True:
			logging.info('load L1 topic from file')
			f = open(l1_topic_path, 'rb')
			self.l1_topics = cPickle.load(f)
			f.close()
		else:
			raise Exception('l1 topics does not exist')
		self.l1_topics = [(key, val) for key, val in self.l1_topics.iteritems()]

if __name__ == '__main__':
	utils.init_logger('log/test_topic_log')
	spider = TopicSpider()
	spider.prepare_work()
	for i in xrange(10):
		data = spider.assign_works()
		status, res = spider.on_assign_works(data)
		spider.receive_work_result(res)