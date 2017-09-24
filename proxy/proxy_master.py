#coding=utf-8
import common.utils
import cPickle
import logging
import ConfigParser
import os
import threading
import sys
import time
from rpc.rpc_client import RPCClient
from rpc.rpc_protocol import rpc_method
import proxy_logic
import crawler.crawl_master as crawl_master

class ProxyProvider(RPCClient):

	def __init__(self, proxy_logic):
		RPCClient.__init__(self)
		self.proxy_logic = proxy_logic

	'''
		与crawler master相连，响应crawler master的代理请求
	'''
	def on_new_client_arrived(self, client_id):
		'''
			通知crawl master我是一个代理服务器
		'''
		self.clients[client_id].i_am_proxy()

	@rpc_method
	def notify_proxy_bad(self, proxy_url):
		self.proxy_logic.notify_proxy_bad(proxy_url)

	@rpc_method
	def get_avail_proxy(self,):
		good_proxy = self.proxy_logic.get_good_proxy()
		logging.info('get_avail_proxy() proxy: %s', repr(good_proxy))
		if good_proxy is not None:
			self.cur_client.on_get_avail_proxy(good_proxy)


if __name__ == '__main__':
	work_dir = os.path.dirname(os.path.abspath(__file__))
	config_file_path = os.path.join(work_dir,'master_config.ini')
	cf = ConfigParser.ConfigParser()
	cf.read(config_file_path)
	ip = cf.get('crawl_slave', 'ip')
	port = cf.get('crawl_slave', 'port')

	logic = proxy_logic.proxy_logic(cf)
	
	proxy_master = crawl_master.CrawlMaster(logic)
	thread_master = threading.Thread(target = lambda : proxy_master.run(cf))
	thread_master.start()

	proxy_provider = ProxyProvider(logic)
	proxy_provider.start_rpc_client(ip, port)
