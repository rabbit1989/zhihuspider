#coding=utf-8	
import urllib2
import logging
import random
from bs4 import BeautifulSoup

def fetch():
	'''
		从代理信息网站爬取新的可用代理
	'''
	logging.info('fetch 31f proxies...')
	l = []
	try:
		req = urllib2.Request('http://31f.cn/https-proxy/')
		html_text = urllib2.urlopen(req,timeout=4).read()
		soup = BeautifulSoup(html_text, 'lxml')
		for tr in soup.findAll('tr'):
			tds = tr.findAll('td')
			if len(tds) < 8:
				continue
			ip = tds[1].text
			port = tds[2].text
			url = ip + ':' + port
			l.append({'url':url, 'type':'https'})
	except Exception, e:
		logging.fatal(e)
	logging.info('31f: fetch %d proxies', len(l))
	return l

if __name__ == '__main__':
	fetch()