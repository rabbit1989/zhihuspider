#coding=utf-8
import common.consts as consts
import urllib2
import logging
import random
from bs4 import BeautifulSoup

def fetch():
	'''
		从代理信息网站爬取新的可用代理
	'''
	logging.info('fetch ssl proxy proxies...')
	l = []
	try:
		agent = consts.http_hds[random.randint(0,len(consts.http_hds)-1)]
		req = urllib2.Request('https://www.sslproxies.org/', headers=agent)
		html_text = urllib2.urlopen(req,timeout=6).read()
		soup = BeautifulSoup(html_text, 'lxml')
		for tr in soup.findAll('tr'):
			tds = tr.findAll('td')
			if len(tds) < 8:
				continue
			ip = tds[0].text
			port = tds[1].text
			url = ip + ':' + port
			if tds[6].text != 'yes':
				continue
			l.append({'url':url, 'type':'https'})
	except Exception, e:
		logging.fatal(e)
	logging.info('us_proxy: fetch %d proxies', len(l))
	return l

if __name__ == '__main__':
	fetch()