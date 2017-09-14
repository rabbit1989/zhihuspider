#coding=utf-8
import utils
import urllib2
import cPickle
import logging
import ConfigParser
import os
import time
import consts
import random
from bs4 import BeautifulSoup

def net_connected(func):
	def wrapper(*args, **kwargs):
		exit_code = os.system('ping www.baidu.com')
		if exit_code:
			logging.fatal('network is disconnected, %s() will not been executed ', func.__name__)
		else:
			func(*args, **kwargs)
	return wrapper


class ProxyMgr:
	def __init__(self,):
		self.proxy_dict = {}
		cf = ConfigParser.ConfigParser()
		cf.read('config.ini')
		self.provider_url = cf.get('proxy', 'provider_url')
		self.log_path = cf.get('proxy', 'log_path')
		self.data_path = cf.get('proxy', 'data_path')
		self.test_url = cf.get('proxy', 'test_url')

	@net_connected
	def fetch_proxy(self,):
		'''
			从代理提供网站爬取新的可用代理
		'''
		if len(self.proxy_dict) > 100:
			logging.warn('num of good proxy in dict exceeds 100, will not fetch new proxy this time')
			return
		try:
			agent = consts.http_hds[random.randint(0,len(consts.http_hds)-1)]
			req = urllib2.Request(self.provider_url, headers=agent)
			html_text = urllib2.urlopen(req,timeout=5).read()
			soup = BeautifulSoup(html_text, 'lxml')
			ip_list = soup.find('table', {'id': 'ip_list'})
			num_ip = 0
			#一次检查10个
			for tr in ip_list.findAll('tr'):
				if tr.attrs.has_key('class') and tr.attrs['class'] != 'subtitle':
					tds = tr.findAll('td')
					if len(tds) < 7:
						continue
					ip = tds[1].text
					port = tds[2].text
					url = ip + ':' + port
					tp = tds[5]
					if self.test_proxy(url, tp) == 'ok' and not self.proxy_dict.has_key(url):
						logging.info('find new good proxy: %s', url)
						self.proxy_dict[url] = {'type':tp, 'status':'ok', 'used':False}
					num_ip += 1
					if num_ip == 10:
						break
			except Exception, e:
				logging.fatal(e)
		logging.info('num of proxy: %d', len(self.proxy_dict))

	@net_connected
	def update_status(self):
		'''
			更新代理列表
		'''
		d = {}
		for url, val in self.proxy_dict.iteritems():
			tp = val['type']
			new_status = self.test_proxy(url, tp)
			if new_status is 'ok':
				val['status'] = new_status
				d[url] = val
		self.proxy_dict = d
		self.dump()


	#rpc method
	def get_avail_proxy(self,):
		for url, val in self.proxy_dict.iteritems():
			if val['status'] == 'ok' and val['used'] == False:
				val['used'] = True
				return {'url':url, 'type':val['type']}
				
	def test_proxy(self, url, tp):
		''' 
			进到这里要确保网络连通，
			先测试代理是否能连通，再通过代理访问测试页面看看是否正常
		'''
		status = None
		#设置代理
		handler = urllib2.ProxyHandler({tp: url})
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)
		resp = urllib2.urlopen(self.test_url, timeout = 7)
		if resp.getcode() == 200:
			status = 'ok'
		else:
			status = 'error'
		logging.info('%s is %s', url, status)
		
		#取消代理
		handler = urllib2.ProxyHandler({})
		opener = urllib2.build_opener(handler)
		urllib2.install_opener(opener)	
		
		return status

	def dump(self):
		f = open(self.data_path, 'wb')
		cPickle.dump(self.proxy_dict, f)
		f.close()

	def load(self):
		f = open(self.data_path, 'rb')
		cPickle.load(self.proxy_dict, f)
		f.close()

	def run(self):
		utils.init_logger(self.log_path)
		while True:
			self.fetch_proxy()
			time.sleep(5)
			self.update_status()
			time.sleep(100)


if __name__ == '__main__':
	proxy_mgr = ProxyMgr()
	proxy_mgr.run()



