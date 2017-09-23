#coding=utf-8
import logging
import threading
import time
import ConfigParser
import common.utils
import os
from rpc.rpc_server import RPCServer
from rpc.rpc_protocol import rpc_method

class CrawlMaster(RPCServer):
	'''
		CrawlMaster负责整体调度
	'''
	def __init__(self, logic = None):
		RPCServer.__init__(self)
		self.slaves_need_proxy = {}
		self.slave_clients = {}
		self.proxy_clients = []
		self.last_proxy_serverd = 0
		self.logic = logic

	def update(self):
		self.logic.prepare_work()
		done = False
		while done is False:
			time.sleep(5)
			#找到空闲的slave
			free_slaves = []
			for slave_client, val in self.slave_clients.iteritems():
				if val == True:
					free_slaves.append(slave_client)		
			logging.info('%d/%d of slaves are free', len(free_slaves), len(self.slave_clients))
			
			#将工作分配给空闲的slave
			for free_slave in free_slaves:
				task = self.logic.assign_works()
				if task == None or len(task) == 0:
					continue
				self.slave_clients[free_slave] = False
				self.clients[free_slave].do_task(task)
		
		logging.info('all works has been assigned!!')

	def run(self, cf):
		common.utils.init_logger(cf.get('log', 'crawl_master_path'))
		if self.logic is None:
			self.logic = common.utils.load_logic_module(cf.get('crawl_master', 'logic_name'))
		port = int(cf.get('crawl_master', 'port'))
		thread = threading.Thread(target=self.update)
		thread.start()
		self.start_rpc_server(port)

	def on_lose_client(self, client_id):
		if client_id in self.proxy_clients:
			self.proxy_clients.remove(client_id)
		elif self.slave_clients.has_key(client_id):
			del self.slave_clients[client_id]

	@rpc_method
	def slave_need_proxy(self):
		self.slaves_need_proxy[self.cur_client_id] = True				
		if len(self.proxy_clients) == 0:
			logging.warn('master: slave_need_proxy(): no proxy client found')
		else:
			num_proxy_client = len(self.proxy_clients)
			self.clients[self.proxy_clients[self.last_proxy_serverd%num_proxy_client]].get_avail_proxy()
			self.last_proxy_serverd = (self.last_proxy_serverd+1)%num_proxy_client

	@rpc_method
	def i_am_proxy(self):
		if not self.cur_client_id in self.proxy_clients:
			self.proxy_clients.append(self.cur_client_id)
			logging.info('master: get new proxy client!: %s', self.cur_client_id)

	@rpc_method
	def i_am_slave(self):
		#先将slave设置成不可用状态，待收到slave传来的通知，再将该slave设置成可用状态
		self.slave_clients[self.cur_client_id] = False

	@rpc_method
	def on_get_avail_proxy(self, proxy):
		if len(proxy) > 0:
			client_satisfied = None
			for client_id in self.slaves_need_proxy.keys():
				if self.slaves_need_proxy[client_id] == True and self.slave_clients.has_key(client_id):
					self.clients[client_id].on_slave_need_proxy(proxy)
					client_satisfied = client_id
					break
			if client_satisfied != None:
				self.slaves_need_proxy[client_satisfied] = False

	@rpc_method
	def on_do_task(self, res):
		logging.info('master: on_do_task()')
		self.logic.receive_work_result(res)

	@rpc_method
	def slave_is_available(self, val):
		self.slave_clients[self.cur_client_id] = val

if __name__ == '__main__':
	work_dir = os.path.dirname(os.path.abspath(__file__))
	config_file_path = os.path.join(work_dir,'config.ini')
	cf = ConfigParser.ConfigParser()
	cf.read(config_file_path)
	crawl_master = CrawlMaster()		
	crawl_master.run(cf)