#coding=utf-8
import logging
import threading
import time
import ConfigParser
import utils
import sys
import Queue
import topic
import urllib2
from rpc.rpc_client import RPCClient
from rpc.rpc_protocol import rpc_method

class CrawlSlave(RPCClient):
	def __init__(self):
		RPCClient.__init__(self)
		self.master_client_id = None
		self.task_queue = Queue.Queue()
		self.topic_spider = topic.TopicSpider()
		self.is_proxy_ok = False

	def update(self):
		task = []
		while True:
			try:
				if self.is_proxy_ok == True:
					if len(task) == 0 and self.task_queue.empty() == False:
						task = self.task_queue.get(block = False)
					if len(task) > 0:
						task_unfinished, output = self.topic_spider.on_assign_works(task)
						if float(len(task_unfinished))/len(task) > 0.5:
							logging.info('slave:update(), proxy is not good, change a good one')
							self.is_proxy_ok = False
							task = task_unfinished
						else:
							task = []
						self.clients[self.master_client_id].on_do_task(output)
				else:
					self.clients[self.master_client_id].slave_need_proxy()		
			except Exception, e:
				logging.fatal(e)

			if self.is_proxy_ok == True and self.task_queue.empty() == True:
				logging.info('waiting for a good proxy...')
				self.clients[self.master_client_id].slave_is_available(True)
			time.sleep(2)


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
		self.clients[self.master_client_id].slave_need_proxy()


	@rpc_method
	def do_task(self, task):
		logging.info('slave::do_task(): get_new_task')	
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
	utils.init_logger(sys.argv[1])
	crawl_slave = CrawlSlave()
	crawl_slave.run()