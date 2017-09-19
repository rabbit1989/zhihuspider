#coding=utf-8
import logging
from twisted.protocols.basic import LineReceiver
import traceback


def rpc_method(func):
	setattr(func, '__isrpc__', True)
	return func

def add_rpc_name(rpc_name, func):
	def wrapper(*args, **kwargs):
		#把rpc_name插入参数表
		func(rpc_name, *args, **kwargs)
	return wrapper

class RPCProtocol(LineReceiver):
	delimiter = '\n'

	def connectionMade(self):
		self.client_id = repr(self.transport.getPeer())
		logging.info('new connection: %s', self.client_id)
		self.factory.clients[self.client_id] = RPCProtocolWrapper(self)
		self.factory.on_new_client_arrived(self.client_id)

	def connectionLost(self, reason):
		logging.warn('connection lost: %s', self.client_id)
		del self.factory.clients[self.client_id]
		self.factory.on_lose_client(self.client_id)
		
	def lineReceived(self, line):
	#	logging.info('receive data: [%s]', line)
		#unpack data
		args_dict = eval(line)
		args = args_dict['args']
		kwargs = args_dict['kwargs']
		self.factory.cur_client = self.factory.clients[self.client_id]
		self.factory.cur_client_id = self.client_id
		self.factory.on_call_rpcmethod(*args, **kwargs)

class RPCProtocolWrapper:
	'''
		写这个类是因为没太弄清楚__getattr__, 原来本来这个类的内容全部在RPCProtocol里面
	'''

	def __init__(self, rpc_proto):
		self.rpc_proto = rpc_proto

	def __getattr__(self, item):
		#如果成员不存在就会进到这里,相当于尝试rpc调用		
		return add_rpc_name(item, self.call_rpcmethod)
		
	def call_rpcmethod(self, *args, **kwargs):
		#pack data
		data = repr({'args':args, 'kwargs':kwargs}) + '\n'
		self.rpc_proto.transport.write(data)

	def get_peer(self):
		return self.rpc_proto.transport.getPeer()