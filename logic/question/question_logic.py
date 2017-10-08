#coding=utf-8
import sys
import common.db as db
import MySQLdb
import logic.logic_base as logic_base
import logging
import ConfigParser
import time
#import crawl_rule
import traceback
import os
import cPickle
import gc
import common.utils
import re
import requests
import json
import urllib2
import time
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

def visit_topic(l, stp_time, proxy):
	headers = {
	'Accept':'*/*',
	'Accept-Encoding':'gzip, deflate, br',
	'Accept-Language':'zh-CN,zh;q=0.8',
	'Connection':'keep-alive',
	'Content-Length':'27',
	'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
	'Cookie':'q_c1=ab2cb6dbc6654bc0b21a31cf68055677|1507206314000|1507206314000; d_c0="AHACuHozewyPTp56I35C5aWt9bE2_BRcnw8=|1507206315"; _zap=a1bf5c12-8662-450f-8f12-f188a0a27f02; aliyungf_tc=AQAAAHjFcjngtAYAaa5cckMO6t0xPxKu; l_cap_id="OTY2NGUzNGQ1NWUyNDE5ODg2MzA1MzE1NjVhZTI0ZTY=|1507345523|6ee0d4d6ac7c2148dc7b4b4054cda13b3b586f50"; r_cap_id="YTM2NjEwMzc0NzMwNGE5OWJkMGFlMzJkZTMwMDg4YjQ=|1507345523|d5c4646e2ffd35089c7ddd261b0e462a4a0c3fca"; cap_id="MzNjNWM4YTViMjViNGE0Yzk3OGUxYWJmOTk3OGU4ZWM=|1507345523|3ddb0bc683fc62746995e4b0094a0716d25cbf01"; __utma=51854390.1375388856.1507206320.1507296811.1507345526.7; __utmb=51854390.0.10.1507345526; __utmc=51854390; __utmz=51854390.1507345526.7.4.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=51854390.000--|2=registration_date=20131105=1^3=entry_date=20171005=1; capsion_ticket="2|1:0|10:1507347214|14:capsion_ticket|44:NzQ1YjE5ODcxMjliNDY5ZTg1NDBjMzM4Y2MyOTcyOTQ=|180220c56ef81585143b872160d067efaf6d3f526a995aed317e9ecc245d7ca2"; z_c0="2|1:0|10:1507347223|4:z_c0|92:Mi4xOV9FZkFBQUFBQUFBY0FLNGVqTjdEQ1lBQUFCZ0FsVk5GOWpfV1FEMnRjUVo3bUppTVZzaGdzWjhrZEw3ZW1rMmxR|156a7536582fc847fa69215a3ef5fbf224ff83ad40446bc22d04d7dc652d4229"; _xsrf=86e41ede-80e9-4ccf-ac3c-8fdf014fb7f5',
	'Host':'www.zhihu.com',
	'Origin':'https://www.zhihu.com',
	'Referer': None,
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
	'X-Requested-With':'XMLHttpRequest',
	'X-Xsrftoken':'86e41ede-80e9-4ccf-ac3c-8fdf014fb7f5'}
	output = []
	failed_input = []
	unique_questions = {}
	for ele in l:
		topic = ele['data']
		try:
			url='https://www.zhihu.com/topic/'+ str(topic) + '/newest'
			headers['Referer'] = url
			qlist = []
			cur_time = time.time()
			past_time = 0
			while past_time <= stp_time:
				resp=requests.post(url,headers = headers,data={'start':0,'offset': cur_time-past_time}, proxies=proxy, timeout = 20)
				msg_dict = json.loads(resp.text)
				logging.info('response msg num: %d', msg_dict['msg'][0])
				soup = BeautifulSoup(msg_dict['msg'][1], 'lxml')
				qlist += soup.findAll('div', {'class':'feed-main'})
				past_time += 700
			num_unique = 0
			for q in qlist:
				link = q.find('a').get('href')
				link = re.search('[0-9]+', link).group()
				if not unique_questions.has_key(link):
					unique_questions[link] = True
					s = list(q.find('h2').strings)
			#		logging.info(s[1] + '  ' + s[3]	+ 'link:' + link) 
					num_unique += 1
					output.append({'type':'topic', 'data':link})
			logging.info('from topic %s find %d questions, %d are unique', topic, len(qlist), num_unique)
		except Exception, e:
			logging.fatal(e)
			failed_input.append(ele)

	return failed_input, output

failed_question = {}
def visit_question(l):
	output = []
	failed_input = []
	for ele in l:
		question_id = ele['data']
		try:
			url='https://www.zhihu.com/question/'+ str(question_id)
			resp, html_text = common.utils.get_response(url)
			if resp == None or html_text == None:
				raise Exception('urllib2 error')
			soup = BeautifulSoup(html_text, 'lxml')
			title_node = soup.find('h1', {'class':'QuestionHeader-title'})
			follow_status_node = soup.find('div', {'class':'QuestionFollowStatus'})
			answer_node = soup.find('h4', {'class':'List-headerText'})
			follow_str = list(follow_status_node.strings)
			answer_str = list(answer_node.strings)
			q = {'id':question_id, 'name':title_node.text, 'focus':follow_str[1], 'view':follow_str[3], 'ans_num':answer_str[0].split(' ')[0]}
			output.append({'type':'question', 'data':q})
			logging.info('%s 关注:%s; 浏览:%s; 回答数:%s' %(q['name'], q['focus'], q['view'], q['ans_num']))
		except Exception, e:
			logging.fatal(e)
			if not failed_question.has_key(question_id):
				failed_question[question_id] = 0
			failed_question[question_id] += 1
			if failed_question[question_id] < 5:
				failed_input.append(ele)
			else:
				failed_question[question_id] = 0

	return failed_input, output

class question_logic(logic_base.logic_base):
	def __init__(self):
		logic_base.logic_base.__init__(self)
		work_dir = os.path.dirname(os.path.abspath(__file__))
		config_file_path = os.path.join(work_dir,'config.ini')
		self.cf = ConfigParser.ConfigParser()
		self.cf.read(config_file_path)
		self.db_conn = db.DBConnection(self.cf)
		self.quest_fetch_time = int(self.cf.get('question', 'quest_fetch_time'))

	def assign_works(self, ):
		'''
			called by crawl master
		'''
		packed_data = []
		tp = None
		data = []
		if len(self.unvisit_topics) > 0:
			tp = 'topic'
			data = self.unvisit_topics[:3]
			self.unvisit_topics = self.unvisit_topics[3:]
			logging.info('num of unvisited topics: %d', len(self.unvisit_topics))
			if self.start_time_topic < 0:
				self.start_time_topic = time.time()
		elif len(self.unvisit_questions) > self.num_visited_questions:
			tp = 'question'
			start = self.num_visited_questions
			end = self.num_visited_questions + 5
			if end > len(self.unvisit_questions):
				end = len(self.unvisit_questions)
			data = self.unvisit_questions[start:end]
			self.num_visited_questions = end
			logging.info('num of total questions: %d; num of visited questions: %d', len(self.unvisit_questions), self.num_visited_questions)
			if self.start_time_question < 0:
				self.start_time_question = time.time()
		elif self.num_visited_questions != 0 and len(self.unvisit_questions) <= self.num_visited_questions:
			#数据全部访问完了，开始第二遍
			self.prepare_work()
		
		if tp != None:
			packed_data = [{'type':tp, 'data':ele} for ele in data]
		return packed_data

	def receive_work_result(self, result):
		'''
			called by crawl master
		'''		
		for ele in result:
			tp = ele['type']
			data = ele['data']
			if tp == 'topic':
				if not self.unique_questions.has_key(data):
					self.unique_questions[data] = True
					self.unvisit_questions.append(data)
			elif tp == 'question':
				cur_time = common.utils.get_sql_time()
				cur_time_sec = int(time.time())
				try:
					sql_str = 'INSERT IGNORE INTO question (question_id, name, focus, view, answer_number, last_visit, last_visit_sec, create_time, visit_interval, focus_inc, view_inc, answer_num_inc)\
					 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE last_visit = %s, visit_interval = %s-last_visit_sec, last_visit_sec = %s, focus_inc = %s-focus, view_inc = %s-view, answer_num_inc = %s-answer_number, focus = %s, view = %s, answer_number = %s'
					self.db_conn.execute(sql_str, [(data['id'], data['name'], data['focus'], data['view'], data['ans_num'], cur_time, str(cur_time_sec), cur_time, '0', '0', '0', '0', cur_time, str(cur_time_sec), str(cur_time_sec), data['focus'], data['view'], data['ans_num'], data['focus'], data['view'], data['ans_num'])])
				except MySQLdb.Error, e:
					self.db_conn.process_exception(e)
		logging.info('receive_work_result: %d results', len(result))
		
	def on_assign_works(self, _input):
		'''
			called by crawl slave
		'''
		logging.info('num of input: %d', len(_input))
		input_unfinished = []
		output = []	
		for ele in _input:
			unfinish = []
			out = []
			if ele['type'] == 'topic':
				unfinish, out = visit_topic([ele], self.quest_fetch_time, self.proxy)
			elif ele['type'] == 'question':
				unfinish, out = visit_question([ele])
			input_unfinished += unfinish
			output += out
		logging.info('%d/%d success', len(_input) - len(input_unfinished), len(_input))
		return input_unfinished, output

	def prepare_work(self, ):
		'''
			called by crawl master
		'''
		logging.info('question_logic: prepare work')
		topic_num = self.cf.get('question', 'topic_num')
		self.unvisit_topics = []
		self.unvisit_questions = []
		self.unique_questions = {}
		self.num_visited_questions = 0
		self.num_received_results = 0
		self.start_time_topic = -1
		self.start_time_question = -1

		try:
			sql_str = 'SELECT * FROM topic ORDER BY focus DESC LIMIT %s' % topic_num
			self.db_conn.execute(sql_str)
			res = self.db_conn.fetch_results()
			self.unvisit_topics = [row[0] for row in res]
		except MySQLdb.Error, e:
			self.db_conn.process_exception(e)

if __name__ == '__main__':
	common.utils.init_logger('log/test_question_log')
	spider = question_logic()
	spider.prepare_work()
	while True:	
		data = spider.assign_works()
		status, res = spider.on_assign_works(data)
		spider.receive_work_result(res)