#coding=utf-8
import common.utils
import crawler.crawl_slave as crawl_slave
import ConfigParser
import sys
import os

if __name__ == '__main__':
	cf = ConfigParser.ConfigParser()
	work_dir = os.path.dirname(os.path.abspath(__file__))
	config_file_path = os.path.join(work_dir,'config.ini')
	cf.read(config_file_path)
	common.utils.init_logger(sys.argv[1])
	crawl_slave = crawl_slave.CrawlSlave()
	crawl_slave.run(cf)