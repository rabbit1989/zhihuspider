#coding=utf-8
import urllib2
import httplib
import common.utils
import threading
import time
import os
import logging
import importlib
import cPickle
import re

def test_proxy(proxy_url, tp, test_url):
	code = 400
	linkid_pattern = re.compile('/[0-9]+')
	try:
		#设置代理
		handler = urllib2.ProxyHandler({tp: proxy_url})
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)
		resp = urllib2.urlopen(test_url, timeout = 20)
		code = resp.getcode()
		actual_url = resp.geturl()
		logging.info('acutal url: '+ actual_url)
		actual_linkid = re.search(linkid_pattern, actual_url).group()[1:]
		text = resp.read()
	except 	urllib2.HTTPError, e:
		code = int(e.code)
		logging.fatal(e)
	except (urllib2.URLError, httplib.HTTPException, IOError) as e:
		logging.fatal(e)
	except Exception, e:
		logging.fatal(e)
		code = 301
	finally:	
		#取消代理
		handler = urllib2.ProxyHandler({})
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)
	logging.info('test_proxy(): code: ' + str(code))
	return code


class proxy_logic:
	def __init__(self, cf = None):
		if cf:
			self.cf = cf
			self.data_path = cf.get('proxy_logic', 'data_path')
			self.test_url = cf.get('proxy_logic', 'test_url')
		#test_url临时写这
		self.test_url = 'https://www.zhihu.com/topic/19550994'
		self.start_time = -1
		self.unique_proxies = {'good':{}, 'checked':{}}
		self.fetch_methods = []
		self.proxies_unverified = []
		self.num_received_results = 0
		self.num_checked_proxies = 0

	def notify_proxy_bad(self, proxy_url):
		logging.info("notify_proxy_bad():" + proxy_url)
		proxy = None
		if self.unique_proxies['good'].has_key(proxy_url):
			proxy = self.unique_proxies['good'][proxy_url]
		else:
			proxy = {'url':proxy_url, 'type':'https'}
		self.proxies_unverified.append(proxy)

	def load_proxy_data(self):
		try:
			f = open(self.data_path, 'rb')
			self.unique_proxies = cPickle.load(f)
			f.close()
			for key, val in self.unique_proxies['good'].iteritems():
				if type(val) != type({}):
					self.unique_proxies['good'][key] = {'type':val}
				self.unique_proxies['good'][key]['used'] = False
				self.unique_proxies['good'][key]['forbid'] = False
				#启动程序时，需要把good proxy 全部检测一遍
				self.proxies_unverified.append({'url':key, 'type':val['type']})
		except Exception, e:
			logging.fatal(e)
			self.unique_proxies = {'good':{}, 'checked':{}}

	def load_fetch_method(self):
		fetch_names = self.cf.get('proxy_logic', 'fetch_method').split(',')
		for name in fetch_names:
			if len(name) > 0:
				logging.info('fetcher name: %s', name)
				self.fetch_methods.append(importlib.import_module('fetch_proxy_methods.' + name))


	def dump_proxy_data(self):
		logging.info('dump proxy dicts')
		f = open(self.data_path, 'wb')
		cPickle.dump(self.unique_proxies, f)
		f.close()

	def fetch_new_proxies(self):
		proxy_list = []
		for fetch_method in self.fetch_methods:
			proxy_list += fetch_method.fetch()
		unique_list = []
		for proxy in proxy_list:
			if not self.unique_proxies['checked'].has_key(proxy['url']):
				unique_list.append(proxy)
				self.unique_proxies['checked'][proxy['url']] = proxy['type']
		self.proxies_unverified += unique_list	
		logging.info('fetch_new_proxies(): %d/%d proxies are unique', len(unique_list) , len(proxy_list))

	def assign_works(self, ):
		'''
			called on crawl master
		'''
		if self.start_time < 0:
			self.start_time = time.time()

		data = self.proxies_unverified[:5]
		self.proxies_unverified = self.proxies_unverified[5:]
		logging.info('proxy_logic: assign_works(): num of unverified proxies: %d ', len(self.proxies_unverified))
		return data

	def on_assign_works(self, _input):
		'''
			called on crawl slave
		'''
		output = []
		num_good = 0
		num_forbid = 0
		for proxy in _input:
			proxy_url = proxy['url']
			code = test_proxy(proxy_url, proxy['type'], self.test_url)
			proxy['used'] = False
			proxy['forbid'] = False

			if code == 200:
				logging.info('proxy %s is good', proxy_url)
				num_good += 1
			elif code < 400:
				proxy['forbid'] = True
				proxy['forbid_start_time'] = time.time()
				if proxy.has_key('forbid_duration'):
					proxy['forbid_duration'] += 1800
				else:
					proxy['forbid_duration'] = 1800
				logging.info('proxy %s is fobiden by the server, cold down for %d min', proxy_url, proxy['forbid_duration']/60)
				num_forbid += 1

			if code < 400:
				output.append((proxy, True))
			else:
				output.append((proxy, False))
			

		logging.info('%d/%d success; %d/%d ok but blocked', num_good, len(_input), num_forbid, len(_input))
		return [], output


	def receive_work_result(self, result):
		'''
			called on crawl master
		'''
		num_result = len(result)
		logging.info('receive work result()')
		self.num_received_results += num_result
		cur_time = time.time()
		#进到这里才算该任务完成了，更新计数器
		self.num_checked_proxies += 5
		for item in result:
			ret = item[1]
			proxy = item[0]
			if ret == True:
				self.unique_proxies['good'][proxy['url']] = proxy
			elif ret == False and self.unique_proxies['good'].has_key(proxy['url']):
				logging.info('delete bad proxy %s from good list', proxy['url'])
				del self.unique_proxies['good'][proxy['url']]
		
		logging.info('process speed so far: check %.1f proxies/min; get %.1f good proxies/min; num of good proxies: %d', self.num_checked_proxies/(cur_time-self.start_time)*60, self.num_received_results/(cur_time-self.start_time)*60, len(self.unique_proxies['good']))

	def get_good_proxy(self):
		for key, val in self.unique_proxies['good'].iteritems():
			if val['used'] == False and (val['forbid'] == False or time.time()-val['forbid_start_time'] > val['forbid_duration']):
				val['used'] = True
				val['forbid'] = False
				return {'url':key, 'type':val['type']}
		return None		
	
	def get_unused_good_proxies(self):
		num_good = 0
		num_cd = 0
		for key, val in self.unique_proxies['good'].iteritems():
			if val['used'] == False:
				num_good += 1
				if val['forbid'] == True:
					num_cd += 1
		logging.info('period_op(): num of unused good proxies: %d, num of cd proxies %d', num_good, num_cd)		

	def period_op(self):
		while True:
			self.dump_proxy_data()
			self.get_unused_good_proxies()
			self.fetch_new_proxies()
			time.sleep(300)

	def prepare_work(self, ):
		'''
			called on crawl master
		'''
		logging.info('proxy logic: prepare work')
		self.load_proxy_data()
		self.load_fetch_method()
		#启动周期执行的线程
		thread = threading.Thread(target=self.period_op)
		thread.start()

if __name__ == '__main__':
	common.utils.init_logger('../log/test_proxylogic_log')
	spider = proxy_logic()
	spider.prepare_work()
	for i in xrange(10):
		data = spider.assign_works()
		status, res = spider.on_assign_works(data)
		spider.receive_work_result(res)