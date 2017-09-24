#coding=utf-8
import urllib2
import common.utils
import threading
import time
import os
import logging
import importlib
import cPickle

def test_proxy(proxy_url, tp):
	status = None
	#设置代理
	handler = urllib2.ProxyHandler({tp: proxy_url})
	opener = urllib2.build_opener(handler)
	urllib2.install_opener(opener)
	test_url = tp+'://www.baidu.com'
	resp = urllib2.urlopen(test_url, timeout = 4)
	if resp.getcode() == 200:
		status = 'ok'
	else:
		status = 'error'
	logging.info('%s is %s', proxy_url, status)
	#取消代理
	handler = urllib2.ProxyHandler({})
	opener = urllib2.build_opener(handler)
	urllib2.install_opener(opener)
	return status


class proxy_logic:
	def __init__(self, cf = None):
		if cf:
			self.cf = cf
			self.data_path = cf.get('proxy_logic', 'data_path')
		self.start_time = -1
		self.unique_proxies = {'good':{}, 'checked':{}}
		self.fetch_methods = []
		self.proxies_unverified = []
		self.num_received_results = 0
		self.num_checked_proxies = 0

	def notify_proxy_bad(self, proxy_url):

		def test():
			try:
				if test_proxy(proxy_url, 'https') == 'ok':
					logging.info('notify_proxy_bad(): proxy %s is still good, reuse it', proxy_url)
					self.unique_proxies['good'][proxy_url]['used'] = False
				else:
					logging.info('notify_proxy_bad(): proxy %s is bad, remove it', proxy_url)
					del self.unique_proxies['good'][proxy_url]
			except Exception, e:
				logging.fatal(e)
				logging.info('notify_proxy_bad(): proxy %s is bad, remove it', proxy_url)
				del self.unique_proxies['good'][proxy_url]
			
		thread = threading.Thread(target = test)
		thread.start()

	def load_proxy_data(self):
		try:
			f = open(self.data_path, 'rb')
			self.unique_proxies = cPickle.load(f)
			f.close()
			for key, val in self.unique_proxies['good'].iteritems():
				if type(val) != type({}):
					self.unique_proxies['good'][key] = {'type':val}
				self.unique_proxies['good'][key]['used'] = False
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
		for proxy in _input:
			try:
				if test_proxy(proxy['url'], proxy['type']) == 'ok':
					output.append(proxy)
			except Exception, e:
				logging.fatal(e)

		logging.info('%d/%d success', len(output), len(_input))
		return [], output


	def receive_work_result(self, result):
		'''
			called on crawl master
		'''
		num_result = len(result)
		logging.info('num of result: %d', num_result)
		self.num_received_results += num_result
		cur_time = time.time()
		#进到这里才算该任务完成了，更新计数器
		self.num_checked_proxies += 5
		for proxy in result:
			self.unique_proxies['good'][proxy['url']] = {'type':proxy['type'], 'used':False}		
		logging.info('process speed so far: check %.1f proxies/min; get %.1f good proxies/min; num of good proxies: %d', self.num_checked_proxies/(cur_time-self.start_time)*60, self.num_received_results/(cur_time-self.start_time)*60, len(self.unique_proxies['good']))

	def get_good_proxy(self):
		for key, val in self.unique_proxies['good'].iteritems():
			if val['used'] == False:
				val['used'] = True
				return {'url':key, 'type':val['type']}
		return None		
	
	def get_unused_good_proxies(self):
		ret = 0
		for key, val in self.unique_proxies['good'].iteritems():
			if val['used'] == False:
				ret += 1
		return ret

	def period_op(self):
		while True:
			self.dump_proxy_data()
			logging.info('period_op(): num of unused good proxies: %d', self.get_unused_good_proxies())
			self.fetch_new_proxies()
			time.sleep(180)

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