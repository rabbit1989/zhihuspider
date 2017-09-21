# /usr/bin/python
# encoding:utf-8

import requests
import json
from bs4 import BeautifulSoup
import sys
import logging
reload(sys)
sys.setdefaultencoding('utf-8')

base_url = 'http://www.ip181.com/'


def fetch():
	logging.info('fetch ip181 proxies...')
	proxy_list = []
	try:
		p = requests.get(base_url)
		requests.encoding = "gb2312"
		html = p.text
		soup = BeautifulSoup(html,"html.parser")
		content = soup.find("tbody")
		tr_list = content.findAll("tr")
		for x in xrange(1,len(tr_list)):
			one_tr = tr_list[x]
			tds = one_tr.findAll("td")
			ip = tds[0].text
			port = tds[1].text
			tps = tds[3].text.lower().split(',')
			if not 'https' in tps:
				continue
			url = ip + ':' + port
			proxy_list.append({'url':url, 'type':tps[1]})
	except Exception, e:
		print e
	finally:
		logging.info('ip181: fetch %d proxies', len(proxy_list))
		return proxy_list

if __name__ == '__main__':
	fetch()