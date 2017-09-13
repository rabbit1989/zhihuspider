#coding=utf-8
from selenium import webdriver
import time
from bs4 import BeautifulSoup
import json
import db
import utils
import logging
import re

def test_auto_click():
	driver = webdriver.Chrome()
	driver.get("http://www.zhihu.com")
	
	cookie = driver.get_cookies()
	print cookie

	driver.find_element_by_link_text('登录').click()
	driver.find_element_by_class_name('signin-switch-password').click()

	driver.find_element_by_name('account').send_keys('galaxysf3@gmail.com') 

	#密码，这里要替换为你的密码
	driver.find_element_by_name('password').send_keys('bgscy1989622')

	#retify_code = input('验证码:')
	#driver.find_element_by_name('captcha').send_keys(retify_code)

	#driver.find_element_by_css_selector('div.button-wrapper.command > button').click()

	time.sleep(20)

	print 'after manual login'
	cookie = driver.get_cookies()
	driver.get('https://www.zhihu.com/topics#运动')

	#def execute_times(times):
	#	for i in range(times + 1):
	#		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	#		time.sleep(5)


	while True:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(1)
		ele = driver.find_elements_by_class_name('zg-btn-white')
		print ele
		if len(ele) <= 1:
			break

	#html=driver.page_source
	#soup1=BeautifulSoup(html,'lxml')
	#authors=soup1.select('a.author-link')
	#authors_alls=[]
	#authors_hrefs=[]
	#for author in authors:
	#	authors_alls.append(author.get_text())
	#	authors_hrefs.append('http://www.zhihu.com'+author.get('href'))
	#authors_intros_urls=soup1.select('span.bio')
	#authors_intros=[]
	#for authors_intros_url in authors_intros_urls:
	#	authors_intros.append(authors_intros_url.get_text())

	#for authors_all,authors_href,authors_intro in zip(authors_alls,authors_hrefs,authors_intros):
	#	data={
	#		'author':authors_all,
	#		'href':authors_href,
	#		'intro':authors_intro
	#	}
	#print(data)

def test_spider():

	f = open('test_data\many_topic.html', 'rb')
	web_page = f.read()
	f.close()
	soup = BeautifulSoup(web_page, 'lxml')
	db_conn = db.DBConnection()

#获取顶层话题	
#	top_topics = soup.select('li.zm-topic-cat-item')
#	topic_links = map(lambda node: node.find('a').get('href'), top_topics)
	
	top_topics = soup.findAll('a', {'href':re.compile('^https://www.zhihu.com/topics#.*')})
	print len(top_topics)

#获取子话题
	sub_topics = soup.findAll('a', attrs={'href':re.compile('.*/topic/[0-9]*')})
	sub_topic_links = map(lambda node : node.get('href'), sub_topics)
	sub_topic_names = map(lambda node : unicode(node.text).strip(' \n'), sub_topics)
	#todo: crawl sub_topic_focus
	sub_topic_focus = range(len(sub_topic_links))
	param_list = []
	cur_time = utils.get_sql_time()
	for i in xrange(len(sub_topic_names)):
		link_str = sub_topic_links[i]
		linkid = link_str[link_str.rfind('/')+1:]
		param_list.append((linkid, sub_topic_names[i], sub_topic_focus[i], cur_time, cur_time))
	logging.info('insert data to db')
	sql_str = 'INSERT IGNORE INTO TOPIC (LINK_ID, NAME, FOCUS, LAST_VISIT, ADD_TIME) VALUES (%s, %s, %s, %s, %s)'
	db_conn.execute(sql_str, param_list)
	logging.info('finished')

def test_h1_string():
	f = open('test_data/test_string.html', 'rb')
	web_page = f.read()
	f.close()
	soup = BeautifulSoup(web_page, 'lxml')
	res = list(soup.find('h1', {'class':'zm-editable-content'}).strings)
	print res


if __name__ == '__main__':
	test_auto_click()
#	test_spider()
#	test_h1_string()
	