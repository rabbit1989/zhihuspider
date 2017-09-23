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
		self.need_proxy = None

	def update(self):
		task = []
		while True:
			time.sleep(3)
			if self.can_do_task() == True:	
				task = self.task_queue.get(block = False)
				task_unfinished, output = self.logic.on_assign_works(task)
				if len(task_unfinished) > 0:
					self.task_queue.put(task_unfinished)

				if float(len(task_unfinished))/len(task) > 0.5:
					logging.info('slave:update(), proxy is not good, want change a good one')
					self.is_proxy_ok = False
				self.clients[self.master_client_id].on_do_task(output)

	def can_do_task(self):
		'''
			判断当前是否可以开始执行任务
		'''
		if self.master_client_id == None:
			logging.warn('slave master lost, do nothing')
			return False
		
		if self.need_proxy == True and self.is_proxy_ok == False:
			logging.warn('waiting for good proxy')
			self.clients[self.master_client_id].slave_need_proxy()
			return False

		if (self.need_proxy == False or self.is_proxy_ok == True) and self.task_queue.empty() == True:
			logging.info('slave is ready to work...')
			if self.master_client_id != None:
				self.clients[self.master_client_id].slave_is_available(True)
			return False
		return True

	def run(self, cf):
		self.logic = common.utils.load_logic_module(cf.get('crawl_slave', 'logic_name'))
		self.need_proxy = cf.get('crawl_slave', 'need_proxy') == 'True'
		master_ip = cf.get('crawl_slave', 'ip')
		master_port = cf.get('crawl_slave', 'port')
		thread = threading.Thread(target = self.update)
		thread.start()
		self.start_rpc_client(master_ip, int(master_port))

	def on_new_client_arrived(self, client_id):
		logging.info('slave: get new client, it must be the crawl master')
		self.master_client_id = client_id
		self.clients[client_id].i_am_slave()
		if self.need_proxy == True:
			self.clients[self.master_client_id].slave_need_proxy()

	def on_lose_client(self, client_id):
		logging.fatal('slave lost connection with master, now it can do nothing')
		self.master_client_id = None

	@rpc_method
	def do_task(self, task):
		if len(task) > 0:
			logging.info('slave::do_task(): get_new_task, push it to queue')
			self.task_queue.put(task)
		else:
			logging.info('slave: task is empty')

	@rpc_method
	def on_slave_need_proxy(self, proxy):
		logging.info('on_slave_need_proxy(): get proxy: %s', repr(proxy))
		if len(proxy) > 0:
			handler = urllib2.ProxyHandler({proxy['type']: proxy['url']})
			opener = urllib2.build_opener(handler)
			urllib2.install_opener(opener)
			self.is_proxy_ok = True

if __name__ == '__main__':
	config_path = sys.argv[1]
	log_path = sys.argv[2]
	common.utils.init_logger(log_path)
	
	cf = ConfigParser.ConfigParser()
	cf.read(config_path)
		
	crawl_slave = CrawlSlave()
	crawl_slave.run(cf)