#coding=utf-8
import logging

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

def load_logic_module(logic_name):
	logging.info('load logic module %s', logic_name)
	logic_module = __import__(logic_name)
	logic_module = getattr(logic_module, logic_name)()
	return logic_module
