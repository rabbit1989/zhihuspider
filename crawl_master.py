#coding=utf-8
import logging
import utils
import threading
import time
import ConfigParser
from rpc.rpc_server import RPCServer
from rpc.rpc_protocol import rpc_method


class CrawlMaster(RPCServer):
	'''
		CrawlMaster负责整体调度
	'''
	def __init__(self):
		RPCServer.__init__(self)
		self.slaves_need_proxy = {}
		self.slave_clients = {}
		self.proxy_client = None

	def update(self):
		while 1:
			time.sleep(20)
			for slave_client in self.slave_clients.keys():
				logging.info('master: let slave do task, slave_id %s', slave_client)
				self.clients[slave_client].do_task()

	def run(self):
		cf = ConfigParser.ConfigParser()
		cf.read('config.ini')
		utils.init_logger(cf.get('log', 'crawl_master_path'))
		port = int(cf.get('crawl_master', 'port'))
		thread = threading.Thread(target=self.update)
		thread.start()
		self.start_rpc_server(port)

	def on_lose_client(self, client_id):
		if self.proxy_client == client_id:
			self.proxy_client = None
		elif self.slave_clients.has_key(client_id):
			del self.slave_clients[client_id]
	
	@rpc_method
	def slave_need_proxy(self):
		client_id = repr(self.cur_client.get_peer())
		self.slaves_need_proxy[client_id] = True				
		if self.proxy_client is None:
			logging.warn('master: slave_need_proxy(): no proxy client found')
			self.cur_client.on_slave_need_proxy({})
		else:
			self.clients[self.proxy_client].get_avail_proxy()

	@rpc_method
	def i_am_proxy(self):
		client_id = repr(self.cur_client.get_peer())
		self.proxy_client = client_id
		logging.info('master: get new proxynode: %s', client_id)

	@rpc_method
	def i_am_slave(self):
		client_id = repr(self.cur_client.get_peer())
		self.slave_clients[client_id] = True

	@rpc_method
	def on_get_avail_proxy(self, proxy):
		client_satisfied = None
		for client_id in self.slaves_need_proxy.keys():
			logging.info('on_get_avail_proxy(): proxy info found, send to slave')
			self.clients[client_id].on_slave_need_proxy(proxy)
			client_satisfied = client_id
			break
		del self.slaves_need_proxy[client_satisfied]

	@rpc_method
	def on_do_task(self, ):
		logging.info('master: on_do_task()')


if __name__ == '__main__':
	crawl_master = CrawlMaster()
	crawl_master.run()