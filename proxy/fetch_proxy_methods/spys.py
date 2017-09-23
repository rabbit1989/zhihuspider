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
	logging.info('fetch spys proxies...')
	l = []
	try:
		for i in range(1, 5):
			agent = consts.http_hds[random.randint(0,len(consts.http_hds)-1)]
			req = urllib2.Request('http://www.xicidaili.com/wn/' + str(i), headers=agent)
			html_text = urllib2.urlopen(req,timeout=4).read()
			soup = BeautifulSoup(html_text, 'lxml')
			ip_list = soup.find('table', {'id': 'ip_list'})
			for tr in ip_list.findAll('tr'):
				if tr.attrs.has_key('class') and tr.attrs['class'] != 'subtitle':
					tds = tr.findAll('td')
					if len(tds) < 7:
						continue
					ip = tds[1].text
					port = tds[2].text
					url = ip + ':' + port
					tp = tds[5].text.lower()
					if tp != 'https':
						continue
					l.append({'url':url, 'type':tp})
	except Exception, e:
		logging.fatal(e)
	return l
	