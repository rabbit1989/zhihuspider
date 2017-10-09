#coding=utf-8
import common.utils
import logging
import ConfigParser
import os
import time
from rpc.rpc_protocol import rpc_method
import proxy_logic
from crawler.crawl_master import CrawlMaster

class ProxyMaster(CrawlMaster):

	def __init__(self, proxy_logic):
		CrawlMaster.__init__(self, proxy_logic)
		self.proxy_logic = proxy_logic

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
	common.utils.init_logger('log/proxy_mgr')
	work_dir = os.path.dirname(os.path.abspath(__file__))
	config_path = os.path.join(work_dir,'config.ini')
	cf = ConfigParser.ConfigParser()
	cf.read(config_path)

	logic = proxy_logic.proxy_logic(cf)	
	proxy_master = ProxyMaster(logic)
	proxy_master.run({'listen_port':cf.get('proxy_master', 'listen_port')})
