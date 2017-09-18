#coding=utf-8
from bs4 import BeautifulSoup
import sys
import cPickle
import re

def process_syps_proxy():
	print 'process_syps_proxy'

	f = open('..\\data\\proxy2', 'rb')
	proxy_dict = cPickle.load(f)
	f.close()

	f = open('..\\data\\proxy_page\\spys_proxy.html')
	html_text = f.read()
	f.close()
	soup = BeautifulSoup(html_text, 'lxml')
	ip_list = soup.findAll('tr', {'class':re.compile('spy1x.')})
	new_proxy = {}
	for line in ip_list:
		tds = line.findAll('td')
		s = list(tds[0].strings)
		ip = s[2]
		port = s[5]
		url = ip+':'+port
		s = list(tds[1].strings)
		proxy_type = (s[0]+s[1]).lower()		
		new_proxy[url] = {'type':proxy_type, 'status':'ok', 'used':False}
	
	proxy_dict.update(new_proxy)
	f = open('..\\data\\proxy2', 'wb')
	cPickle.dump(proxy_dict, f)
	f.close()

if __name__ == '__main__':
	if sys.argv[1] == 'spys':
		process_syps_proxy()
