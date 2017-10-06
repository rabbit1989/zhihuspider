#coding=utf-8	
#import common.consts as consts
import logging
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
import sys
import os
import test_question
import json
import time
reload(sys)
sys.setdefaultencoding('utf8')

#wb = webdriver.Chrome()

def test():
	l = []
	try:	
		url = 'https://www.zhihu.com'
		post_data = {'_xsrf':'374ae6712d388f8134c6312c2c4ab1d7', 'password':'bgscy89622', 'captcha_type':'cn', 'email':'galaxysf3@gmail.com'}
		r = requests.post(url, data = post_data, timeout=20)
		f = open('return_page.html', 'wb')
		f.write(r.text)
		f.close()
		work_dir = os.path.dirname(os.path.abspath(__file__))
		html_path = os.path.join(work_dir,'test.html')
		wb.get('file:///' + html_path)

	except Exception, e:
		print e

#if __name__ == '__main__':
#	test()


import cookielib
import Cookie
import urllib2
 
def build_opener_with_cookie_str(cookie_str, domain, path='/'):
	simple_cookie = Cookie.SimpleCookie(cookie_str)    # Parse Cookie from str
	cookiejar = cookielib.CookieJar()    # No cookies stored yet
 
	for c in simple_cookie:
		cookie_item = cookielib.Cookie(
			version=0, name=c, value=str(simple_cookie[c].value),
					 port=None, port_specified=None,
					 domain=domain, domain_specified=None, domain_initial_dot=None,
					 path=path, path_specified=None,
					 secure=None,
					 expires=None,
					 discard=None,
					 comment=None,
					 comment_url=None,
					 rest=None,
					 rfc2109=False,
			)
		cookiejar.set_cookie(cookie_item)    # Apply each cookie_item to cookiejar
	return urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))    # Return opener


def test_urllib2():
	cookie_str = 'q_c1=ab2cb6dbc6654bc0b21a31cf68055677|1507206314000|1507206314000; d_c0="AHACuHozewyPTp56I35C5aWt9bE2_BRcnw8=|1507206315"; _zap=a1bf5c12-8662-450f-8f12-f188a0a27f02; aliyungf_tc=AQAAAKlN/U9SoA0Aaa5cckv6V1EFU/hQ; r_cap_id="N2ExZDhkYjc3ZGI1NGU0Y2JhOTM5YmI5NTNmMTI5M2E=|1507278715|92b4735f1eb31b1cb0e8e624408af1e668abeb31"; cap_id="OWViOGNhNjdiZjQ2NDU2MGE3NjA4ZTFmZTlmYzU3M2Y=|1507278715|69908ec5ff78fc2d5fb6bb9e38ad19258103de89"; z_c0=Mi4xOV9FZkFBQUFBQUFBY0FLNGVqTjdEQmNBQUFCaEFsVk4wYzctV1FBSF8xSkhJU1RhaWFrM1dmX0h0cmpaNS1oQk9B|1507279313|81a3d726be3aff0859b6fcc9d41608c0dee5c22a; __utma=51854390.1375388856.1507206320.1507216588.1507276880.4; __utmb=51854390.0.10.1507276880; __utmc=51854390; __utmz=51854390.1507206320.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=51854390.100-1|2=registration_date=20131105=1^3=entry_date=20131105=1; _xsrf=ca29f01a-ad0a-423a-8bb6-19b5d82ab0f8'

	opener = build_opener_with_cookie_str(cookie_str, domain='www.zhihu.com')	
	opener.addheaders = [('Content-Length', '27')]
	html_doc = opener.open('https://www.zhihu.com/topic/19550429/newest').read()
	f = open('return_page.html', 'wb')
	f.write(html_doc)
	f.close()

def test_request():
	url="https://www.zhihu.com/topic/19550429/newest"
	headers = {
		'Accept':'*/*',
		'Accept-Encoding':'gzip, deflate, br',
		'Accept-Language':'zh-CN,zh;q=0.8',
		'Connection':'keep-alive',
		'Content-Length':'27',
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'Cookie':'q_c1=ab2cb6dbc6654bc0b21a31cf68055677|1507206314000|1507206314000; d_c0="AHACuHozewyPTp56I35C5aWt9bE2_BRcnw8=|1507206315"; _zap=a1bf5c12-8662-450f-8f12-f188a0a27f02; aliyungf_tc=AQAAAKlN/U9SoA0Aaa5cckv6V1EFU/hQ; r_cap_id="N2ExZDhkYjc3ZGI1NGU0Y2JhOTM5YmI5NTNmMTI5M2E=|1507278715|92b4735f1eb31b1cb0e8e624408af1e668abeb31"; cap_id="OWViOGNhNjdiZjQ2NDU2MGE3NjA4ZTFmZTlmYzU3M2Y=|1507278715|69908ec5ff78fc2d5fb6bb9e38ad19258103de89"; z_c0=Mi4xOV9FZkFBQUFBQUFBY0FLNGVqTjdEQmNBQUFCaEFsVk4wYzctV1FBSF8xSkhJU1RhaWFrM1dmX0h0cmpaNS1oQk9B|1507279313|81a3d726be3aff0859b6fcc9d41608c0dee5c22a; __utma=51854390.1375388856.1507206320.1507216588.1507276880.4; __utmb=51854390.0.10.1507276880; __utmc=51854390; __utmz=51854390.1507206320.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmv=51854390.100-1|2=registration_date=20131105=1^3=entry_date=20131105=1; _xsrf=ca29f01a-ad0a-423a-8bb6-19b5d82ab0f8',
		'Host':'www.zhihu.com',
		'Origin':'https://www.zhihu.com',
		'Referer':'https://www.zhihu.com/topic/19550429/newest',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
		'X-Requested-With':'XMLHttpRequest',
		'X-Xsrftoken':'ca29f01a-ad0a-423a-8bb6-19b5d82ab0f8'}

	re=requests.post(url,headers = headers,data={'start':0,'offset': time.time()-3800})
#	f = open('return_page.html', 'wb')
#	f.write(re.text)
#	f.close()
	msg_dict = json.loads(re.text)
	print 'msg num: ' + str(msg_dict['msg'][0])
	test_question.test_question(msg_dict['msg'][1])

if __name__ == '__main__':
	test_request()
#    import re
#    print 'Open With Cookie:', re.search('<title>(.*?)</title>', html_doc, re.IGNORECASE).group(1)
 
#    html_doc = urllib2.urlopen('http://192.168.1.253').read()
#    print 'Open Without Cookie:', re.search('<title>(.*?)</title>', html_doc, re.IGNORECASE).group(1)