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
		self.client = None

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
		reactor.listenTCP(port, self)
		reactor.run()

