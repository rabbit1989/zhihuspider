#coding=utf-8
import common.utils
import urllib2
import cPickle
import logging
import ConfigParser
import os
import common.consts as consts
import random
import threading
import sys
import time
from rpc.rpc_client import RPCClient
from rpc.rpc_protocol import rpc_method
from bs4 import BeautifulSoup

def net_connected(func):
	def wrapper(*args, **kwargs):
		exit_code = os.system('ping www.baidu.com')
		if exit_code:
			logging.fatal('network is disconnected, %s() will not been executed ', func.__name__)
		else:
			func(*args, **kwargs)
	return wrapper


class ProxyMgr(RPCClient):
	def __init__(self, proxy_id):
		RPCClient.__init__(self)
		self.proxy_dict = {}
		work_dir = os.path.dirname(os.path.abspath(__file__))
		config_file_path = os.path.join(work_dir,'config.ini')
		self.cf = ConfigParser.ConfigParser()
		self.cf.read(config_file_path)
		self.provider_url = self.cf.get('proxy'+proxy_id, 'provider_url')
		self.data_path = self.cf.get('proxy'+proxy_id, 'data_path')
		self.test_url = self.cf.get('proxy'+proxy_id, 'test_url')
		self.log_path = self.cf.get('proxy'+proxy_id, 'proxy_path')
		self.load_proxy_data()

	@net_connected
	def fetch_proxy(self,):
		'''
			从代理信息网站爬取新的可用代理
		'''
		logging.info('fetch_proxy()...')
		if len(self.proxy_dict) > 200:
			logging.warn('num of good proxy in dict exceeds 100, will not fetch new proxy this time')
			return
		try:
			agent = consts.http_hds[random.randint(0,len(consts.http_hds)-1)]
			req = urllib2.Request(self.provider_url, headers=agent)
			html_text = urllib2.urlopen(req,timeout=4).read()
			soup = BeautifulSoup(html_text, 'lxml')
			ip_list = soup.find('table', {'id': 'ip_list'})
			for tr in ip_list.findAll('tr'):
				if tr.attrs.has_key('class') and tr.attrs['class'] != 'subtitle':
					tds = tr.findAll('td')
					if len(tds) < 7:
						continue
					ip = tds[1].text
					port = tds[2].text
					url = ip + ':' + port
					tp = tds[5].text.lower()
					if tp != 'https':
						continue
					try:
						if not self.proxy_dict.has_key(url) and self.test_proxy(url, tp) == 'ok':
							logging.info('fetch_proxy():find new good proxy: %s', url)
							self.proxy_dict[url] = {'type':tp, 'status':'ok', 'used':False}
					except Exception, e:
						logging.fatal(e)
		except Exception, e:
			logging.fatal(e)
		logging.info('num of good proxy: %d', len(self.proxy_dict))

	@net_connected
	def update_status(self):
		'''
			更新代理列表
		'''
		logging.info('update proxy()...')
		d = {}
		for url, val in self.proxy_dict.iteritems():
			try:
				tp = val['type']
				new_status = self.test_proxy(url, tp)
				if new_status == 'ok':
					val['status'] = new_status
					d[url] = val
				logging.info('update_status():%s is still %s', url, new_status)
			except Exception, e:
				logging.fatal(e)
		self.proxy_dict = d
		
	def test_proxy(self, url, tp):
		''' 
			进到这里要确保网络连通，否则测试没意义
		'''
		status = None
		#设置代理
		handler = urllib2.ProxyHandler({tp: url})
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)
		url = tp+'://'+self.test_url
		resp = urllib2.urlopen(url, timeout = 7)
		if resp.getcode() == 200:
			status = 'ok'
		else:
			status = 'error'
		
		#取消代理
		handler = urllib2.ProxyHandler({})
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)	
		
		return status

	def dump_proxy_data(self):
		logging.info('dump proxy dicts')
		f = open(self.data_path, 'wb')
		cPickle.dump(self.proxy_dict, f)
		f.close()

	def load_proxy_data(self):
		try:
			f = open(self.data_path, 'rb')
			self.proxy_dict = cPickle.load(f)
			f.close()
			#把'used'全部设为False
			for url, val in self.proxy_dict.iteritems():
				val['used'] = False
		except Exception, e:
			logging.fatal(e)
			self.proxy_dict = {}

	def update(self):
		while True:
	#		self.update_status()
			self.fetch_proxy()

	def period_dump(self):
		while True:
			self.dump_proxy_data()
			time.sleep(60)

	def run(self):
		common.utils.init_logger(self.log_path)
		thread_update = threading.Thread(target = self.update)
		thread_update.start()

		thread_dump = threading.Thread(target = self.period_dump)
		thread_dump.start()

		ip = self.cf.get('crawl_master', 'ip')
		port = self.cf.get('crawl_master', 'port')
		self.start_rpc_client(ip, int(port))

	def on_new_client_arrived(self, client_id):
		'''
			通知crawl master我是一个代理服务器
		'''
		self.clients[client_id].i_am_proxy()

	@rpc_method
	def get_avail_proxy(self,):
		proxy_id = None
		proxy = {}
		for url, val in self.proxy_dict.iteritems():
			if val['status'] == 'ok' and val['used'] == False:
				proxy_id = url
				break
		if proxy_id is not None:
			proxy = {'url':proxy_id, 'type':val['type']}
			self.proxy_dict[proxy_id]['used'] = True
		logging.info('get_avail_proxy() proxy: %s', repr(proxy))
		self.cur_client.on_get_avail_proxy(proxy)

if __name__ == '__main__':
	#参数argv[1]填1或2，表示proxy_mgr的id
	proxy_mgr = ProxyMgr(sys.argv[1])
	proxy_mgr.run()



