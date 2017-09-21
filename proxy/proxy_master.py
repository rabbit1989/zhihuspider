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
	'''
		与crawler master相连，响应crawler master的代理请求
	'''
	def on_new_client_arrived(self, client_id):
		'''
			通知crawl master我是一个代理服务器
		'''
		self.clients[client_id].i_am_proxy()

	@rpc_method
	def remove_bad_proxy(self, proxy_url):
		pass

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
	logic = proxy_logic.proxy_logic()
#	proxy_provider = ProxyProvider(logic)
#	thread_provider = threading.Thread(target = lambda : proxy_provider.run())
#	thread_provider.start()
	
	work_dir = os.path.dirname(os.path.abspath(__file__))
	config_file_path = os.path.join(work_dir,'config.ini')
	cf = ConfigParser.ConfigParser()
	cf.read(config_file_path)
	
	proxy_master = crawl_master.CrawlMaster(logic)
	proxy_master.run(cf)
	



