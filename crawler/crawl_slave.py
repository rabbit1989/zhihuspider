#coding=utf-8
import logging
import threading
import time
import ConfigParser
import common.utils 
import sys
import os
import Queue
import urllib2
from rpc.rpc_client import RPCClient
from rpc.rpc_protocol import rpc_method

class CrawlSlave(RPCClient):
	def __init__(self):
		RPCClient.__init__(self)
		self.master_client_id = None
		self.task_queue = Queue.Queue()
		self.logic = None
		self.is_proxy_ok = False

	def update(self):
		task = []
		while True:
			time.sleep(2)
			if self.master_client_id == None:
				continue

			if self.is_proxy_ok == False:
				logging.warn('waiting for good proxy')
				self.clients[self.master_client_id].slave_need_proxy()		
				continue
				
			try:
				task += self.task_queue.get(block = False)
			except Exception, e:
				logging.fatal(e)

			if len(task) > 0:
				task_unfinished, output = self.logic.on_assign_works(task)
				
				if float(len(task_unfinished))/len(task) > 0.5:
					logging.info('slave:update(), proxy is not good, want change a good one')
					self.is_proxy_ok = False
				task = task_unfinished
				self.clients[self.master_client_id].on_do_task(output)

			if self.is_proxy_ok == True and self.task_queue.empty() == True:
				logging.info('slave is ready to work...')
				self.clients[self.master_client_id].slave_is_available(True)

	def run(self):
		cf = ConfigParser.ConfigParser()
		work_dir = os.path.dirname(os.path.abspath(__file__))
		config_file_path = os.path.join(work_dir,'config.ini')
		cf.read(config_file_path)
		self.logic = common.utils.load_logic_module(cf.get('crawl_master', 'logic_name'))
		master_ip = cf.get('crawl_master', 'ip')
		master_port = cf.get('crawl_master', 'port')
		thread = threading.Thread(target = self.update)
		thread.start()
		self.start_rpc_client(master_ip, int(master_port))

	def on_new_client_arrived(self, client_id):
		logging.info('slave: get new client, it must be the crawl master')
		self.master_client_id = client_id
		self.clients[client_id].i_am_slave()
		self.clients[self.master_client_id].slave_need_proxy()

	def on_lose_client(self, client_id):
		logging.fatal('slave lost connection with master, now it can do nothing')
		slef.master_client_id = None

	@rpc_method
	def do_task(self, task):
		logging.info('slave::do_task(): get_new_task, push it to queue')	
		self.task_queue.put(task)

	@rpc_method
	def on_slave_need_proxy(self, proxy):
		logging.info('on_slave_need_proxy(): get proxy: %s', repr(proxy))
		if len(proxy) > 0:
			handler = urllib2.ProxyHandler({proxy['type']: proxy['url']})
			opener = urllib2.build_opener(handler)
			urllib2.install_opener(opener)
			self.is_proxy_ok = True

if __name__ == '__main__':
	common.utils.init_logger(sys.argv[1])
	crawl_slave = CrawlSlave()
	crawl_slave.run()