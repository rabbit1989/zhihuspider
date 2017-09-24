#coding=utf-8	
#import common.consts as consts
import logging
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import sys
import os
reload(sys)
sys.setdefaultencoding('utf8')

wb = webdriver.Chrome()

def fetch():
	'''
		从代理信息网站爬取新的可用代理
	'''
	logging.info('fetch spys proxies...')
	l = []
	try:	
		#先用requests post数据，保存到本地，然后用selenim.webdriver打开本地文件，渲染后再获取需要的代理数据
		#如果不用浏览器内核渲染网页，代理端口号出不来
		url = 'http://spys.one/en/https-ssl-proxy/'
		post_data = {'xpp':'5', 'xf1':'0', 'xf4':'0', 'xf5':'0'}
		r = requests.post(url, data = post_data, timeout=20)
		f = open('proxy\\fetch_proxy_methods\\test.html', 'wb')
		f.write(r.text)
		f.close()
		work_dir = os.path.dirname(os.path.abspath(__file__))
		html_path = os.path.join(work_dir,'test.html')
		wb.get('file:///' + html_path)
		html_text = wb.page_source

		soup = BeautifulSoup(html_text, 'lxml')
		ip_list = soup.findAll('tr', {'class':re.compile('spy1xx*')})
		
		#跳过title
		ip_list = ip_list[1:]
		for line in ip_list:
			tds = line.findAll('td')
			s = list(tds[0].strings)
			ip = s[2]
			port = s[5]
			url = ip+':'+port
			s = list(tds[1].strings)
			proxy_type = (s[0]+s[1]).lower()	
			if proxy_type == 'https':
				l.append({'url':url, 'type':'https'})
		logging.info('fetch %d proxies', len(l))

	except Exception, e:
		logging.fatal(e)
	return l