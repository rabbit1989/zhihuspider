#coding=utf-8
import common.utils
import crawler.crawl_slave as crawl_slave
import sys
import os
import ConfigParser

if __name__ == '__main__':
	
	if len(sys.argv) != 2:
		print u'请输入日志路径!'
		exit(-1)

	work_dir = os.path.dirname(os.path.abspath(__file__))
	config_path = os.path.join(work_dir,'config.ini')
	log_path = sys.argv[1]
	common.utils.init_logger(log_path)
	
	cf = ConfigParser.ConfigParser()
	cf.read(config_path)
	logic_name = cf.get('proxy_slave', 'logic_name')
	connect_ip = cf.get('proxy_slave', 'connect_ip')
	connect_port = cf.get('proxy_slave', 'connect_port')
	need_proxy = cf.get('proxy_slave', 'need_proxy') == 'True'
	cs = crawl_slave.CrawlSlave()
	cs.run({'logic_name':logic_name, 'connect_port':connect_port, 'connect_ip':connect_ip, 'need_proxy':need_proxy})