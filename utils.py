#coding=utf-8
from datetime import datetime
import ConfigParser
import logging
import sys
import time
import random
import urllib2
import copy
from bs4 import BeautifulSoup

def get_sql_time():
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def init_logger():
	cf = ConfigParser.ConfigParser()
	cf.read("config.ini")
	logging.basicConfig(level=logging.INFO, 
			format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
			datefmt='%A, %Y-%m-%d %H:%M:%S', 
			filename= cf.get('log', 'file_name'), 
			filemode = 'w')
	console = logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)

def get_links(bs, rule):
	nodes = rule(bs)
	return map(lambda node : copy.copy(node.get('href')), nodes)
			

#将list 分成相等的几部分
def split_list(l, num_part):
	res = []
	for i in xrange(num_part):
		n = len(l)/num_part
		start = i*n
		end = (i+1)*n
		if i == num_part-1:
			end = len(l)
		res.append(l[start:end])
	return res

#将dict 分成相等的几部分
def split_dict(d, num_part):
	l = [(key, val) for key, val in d.iteritems()]
	l_split = split_list(l, num_part)
	res = []
	for i in xrange(num_part):
		d_split = {}
		for ele in l_split[i]:
			d_split[ele[0]] = ele[1]
		res.append(d_split)
	return res

def split_data(data, num_part):
	if isinstance(data, list) == True:
		return split_list(data, num_part)
	elif isinstance(data, dict) == True:
		return split_dict(data, num_part)
	else:
		raise Exception('split_data: unknown data type')

def merge_data(data_list):
	if isinstance(data_list[0], list) == True:
		raise NotImplementedError
	elif isinstance(data_list[0], dict) == True:
		return merge_dict(data_list)
	else:
		raise Exception('merge_data: unknown data type')

def select_subset(data, num):
	if isinstance(data, list) == True:
		return random.sample(data, num)
	elif isinstance(data, dict) == True:
		d = {}
		i = 0
		for key, val in data.iteritems():
			d[key] = val
			i+=1
			if i == num:
				break
		return d
	else:
		raise Exception('select_subset: unknown data type')

def merge_dict(data_list):
	d = {}
	for data_dict in data_list:
		d.update(data_dict)
	return d

def add_new_topics(topic_links, topic_dict):
	cur_time = get_sql_time()
	for topic_link in topic_links:
		linkid = copy.copy(topic_link[topic_link.rfind('/')+1:])
		if not topic_dict.has_key(linkid):
			topic_dict[linkid] = {'name':None, 'focus':None, 'last_visit':cur_time, 'add_time':cur_time}

def get_soup(wd, url, scroll_end = False, times = sys.maxint):
	'''
		通过webdriver获取网页内容，然后生成bs对象
	'''
	cur_time = 0
	while cur_time < times:
		wd.get_page(url, scroll_end)
		page_text = wd.page_source()
		if page_text is None or len(page_text) <= 1:
			logging.fatal('fetch url %s failed', url)
			time.sleep(0.5)
			cur_time += 1
		else:
			break

	return BeautifulSoup(wd.page_source(), 'lxml')


hds=[{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},\
	{'User-Agent':'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},\
	{'User-Agent':'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'},\
	{'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'},\
	{'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'},\
	{'User-Agent':'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
	{'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'},\
	{'User-Agent':'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'},\
	{'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
	{'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'},\
	{'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'},\
	{'User-Agent':'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'},\
	{'User-Agent':'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

def get_soup_request(url):
	'''
		通过Request工具获取网页，然后生成bs对象
	'''
	agent = hds[random.randint(0,len(hds)-1)]
	req = urllib2.Request(url,headers=agent)
	plain_text = urllib2.urlopen(req,timeout=7).read()
	return BeautifulSoup(plain_text, 'lxml')

def save_page(_id, page_text):
	f = open('err_pages/' + str(_id) + '.html', 'wb')
	f.weite(page_text)
	f.close()		