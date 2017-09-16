#coding=utf-8
import logging
import threading
import time
import ConfigParser
import utils
import sys
from rpc.rpc_client import RPCClient
from rpc.rpc_protocol import rpc_method

class CrawlSlave(RPCClient):
	def __init__(self):
		RPCClient.__init__(self)
		self.master_client_id = None

	def update(self):
		while True:
			time.sleep(20)
			#向master请求代理
			logging.info('update: need_proxy()')
			self.clients[self.master_client_id].slave_need_proxy()
			
	def run(self):
		cf = ConfigParser.ConfigParser()
		cf.read('config.ini')
		master_ip = cf.get('crawl_master', 'ip')
		master_port = cf.get('crawl_master', 'port')

		thread = threading.Thread(target = self.update)
		thread.start()
		self.start_rpc_client(master_ip, int(master_port))

	def on_new_client_arrived(self, client_id):
		logging.info('slave: get new client')
		self.master_client_id = client_id
		self.clients[client_id].i_am_slave()


	@rpc_method
	def do_task(self):
		logging.info('do_task()')
		self.cur_client.on_do_task()

	@rpc_method
	def on_slave_need_proxy(self, proxy):
		logging.info('on_slave_need_proxy(): get proxy: %s', repr(proxy))

if __name__ == '__main__':
	utils.init_logger(sys.argv[1])
	crawl_slave = CrawlSlave()
	crawl_slave.run()