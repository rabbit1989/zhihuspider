#coding=utf-8
import logging
from twisted.internet.protocol import ServerFactory
from twisted.internet import reactor
import rpc_protocol


class RPCServer(ServerFactory):
	protocol = rpc_protocol.RPCProtocol

	def __init__(self):
		self.clients = {}
		#这种方式有问题，但目前还没出错，暂时这样吧
		self.cur_client = None

	def on_new_client_arrived(self, client_id):
		'''
			新客户端连接后，如需要进行一些操作，请重写该方法
		'''
		logging.info('RPCServer: on_new_client_arrived %s', client_id)

	def on_lose_client(self, client_id):
		'''
			客户端丢失连接后，如需进行一些善后，请重写该方法
		'''
		logging.info('RPCServer: on_lose_client%s', client_id)
		
	def on_call_rpcmethod(self, rpc_method, *args, **kwargs):
		if hasattr(self, rpc_method):
			func = getattr(self, rpc_method)
			if not hasattr(func, '__isrpc__'):
				logging.fatal('%s is not a rpc method, do nothing!', rpc_method)
				return
			getattr(self, rpc_method)(*args, **kwargs)
		else:
			logging.fatal('rpc method %s not exist, do nothing', rpc_method)

	def start_rpc_server(self, port):
		'''
			run函数是阻塞的，请在完成其他所有工作后再调用
		'''
		reactor.listenTCP(int(port), self)
		if not reactor.running:
			reactor.run()

