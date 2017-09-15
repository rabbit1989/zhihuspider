#coding=utf-8
import logging
from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
import rpc_protocol

class RPCClient(ClientFactory):
	protocol = rpc_protocol.RPCProtocol
	
	def __init__(self):
		self.clients = {}
		self.client = None

	def startedConnecting(self, connector):
		logging.info('Started to connect.')

#	def buildProtocol(self, addr):
#		logging.info(str(addr), ' connected.')

	def clientConnectionLost(self, connector, reason):
		logging.info('Lost connection, reason: %s', reason)

	def clientConnectionFailed(self, connector, reason):
		logging.info('Connection failed .Reason: %s', reason)

	def on_call_rpcmethod(self, rpc_method, *args, **kwargs):
		if hasattr(self, rpc_method):
			func = getattr(self, rpc_method)
			if not hasattr(func, '__isrpc__'):
				print '%s is not a rpc method, do nothing!'% rpc_method
			#	logging.fatal('%s is not a rpc method, do nothing!', rpc_method)
				return
			getattr(self, rpc_method)(*args, **kwargs)
		else:
			raise Exception('rpc method %s not exist', rpc_method)

	def start_rpc_client(self, ip, port):
		'''
			run函数是阻塞的，请在完成其他所有工作后再调用
		'''
		reactor.connectTCP(ip, port, self)
		reactor.run()


