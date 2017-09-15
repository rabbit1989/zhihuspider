#coding=utf-8
import rpc_server
import rpc_client
from rpc_protocol import rpc_method
import threading
import sys
import time
import logging

class TestServer(rpc_server.RPCServer):

	@rpc_method
	def is_proxy_good(self, ip, port):
		logging.info('server:proxy %s:%s is good',ip, str(port))
		self.client.on_is_proxy_good('proxy is velly velly good!')

	def i_am_not_rpc(self, ip, port):
		logging.fatal('server: ooops! it\'s impossible to reach here!')

class TestClient(rpc_client.RPCClient):

	@rpc_method
	def on_is_proxy_good(self, msg):
		logging.info('client: receive msg from server: %s', msg)


def func(client):
	while 1:
		time.sleep(5)
		for _client_id, _client in client.clients.iteritems():
			logging.info('client: call rpc method is_proxy_good')
			_client.is_proxy_good('192.168.1.1', 1000)
			_client.is_proxy_bad('192.168.2.3', 3232)
			_client.i_am_not_rpc('12312.123.123.23', 1312)

def test_server():
	init_logger('log_server')
	server_side = TestServer()
	server_side.start_rpc_server(9999)

def test_client():
	init_logger('log_client')
	client_side = TestClient()
	thread = threading.Thread(target = func, args=(client_side,))
	thread.start()
	client_side.start_rpc_client('127.0.0.1', 9999)

def init_logger(log_path):
	logging.basicConfig(level=logging.INFO, 
			format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
			datefmt='%A, %Y-%m-%d %H:%M:%S', 
			filename= log_path, 
			filemode = 'w')
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)


if __name__ == '__main__':
	if sys.argv[1] == 'server':
		test_server()	
	else:
		test_client()
