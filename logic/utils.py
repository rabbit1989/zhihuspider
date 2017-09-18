#coding=utf-8
from datetime import datetime
import logging
import time
import random
import urllib2
import copy
import sys
import common.consts as consts
from bs4 import BeautifulSoup

def get_sql_time():
	return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

def add_new_topics(topic_links, topic_list, unique_topic_set):
	cur_time = get_sql_time()
	for topic_link in topic_links:
		linkid = copy.copy(topic_link[topic_link.rfind('/')+1:])
		if not unique_topic_set.has_key(linkid):
			unique_topic_set[linkid] = True
			topic_list.append((linkid, {'name':None, 'focus':None, 'last_visit':cur_time, 'add_time':cur_time, 'expend':False})) 

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


def get_soup_request(url):
	'''
		通过Request工具获取网页，然后生成bs对象
	'''
	agent = consts.http_hds[random.randint(0,len(consts.http_hds)-1)]
	req = urllib2.Request(url,headers=agent)
	plain_text = urllib2.urlopen(req,timeout=7).read()
	return BeautifulSoup(plain_text, 'lxml')

def get_response(url):
	agent = consts.http_hds[random.randint(0,len(consts.http_hds)-1)]
	req = urllib2.Request(url,headers=agent)
	return urllib2.urlopen(req,timeout=15)


def save_page(_id, page_text):
	f = open('err_pages/' + str(_id) + '.html', 'wb')
	f.weite(page_text)
	f.close()