#coding=utf-8
#本文件包含爬虫爬取具体字段的规则，规则可能会随着网站升级而改变，
#把规则整理在一个文件里，而不是硬编码
import re
import copy

def top_topics(bs):
	'''
		获取顶层话题
	'''
	res = bs.findAll('a', {'href':re.compile('^https://www.zhihu.com/topics#.*')})
	if len(res) == 0:
		res = bs.findAll('a', {'href':re.compile('^#.*')})
	return res

def sub_topics(bs):
	'''
		获取子话题
	'''
	return bs.findAll('a', attrs={'href':re.compile('.*/topic/[0-9]*')})

def topic_name(bs):
	'''
		获取话题名字
	'''
	return copy.copy(list(bs.find('h1', {'class':'zm-editable-content'}).strings)[0])

def topic_focus(bs, topic_id):
	'''
		话题关注人数
	'''
	node = bs.find('a', attrs={'href':re.compile('.*/topic/'+topic_id+'/followers$')})
	if node is not None:
		return node.text
	return copy.copy(list(bs.find('div', {'class':'zm-topic-side-followers-info'}).strings)[1])

def l2_topics(bs):
	'''
		在l1 topic页面上出现的相关话题
	'''
	return bs.findAll('a', {'href' : re.compile('^/topic/[0-9]*$')})
