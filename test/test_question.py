#coding=utf-8
import urllib2
import re
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf8')


def change_time(time_str):
	if time_str == u'刚刚':
		return 0
	num = int(re.findall('\d+', time_str)[0])
	if time_str.find(u'小时') != -1:
		num *= 60
	return num

def test_question(html_text):
#	resp = urllib2.urlopen(url, timeout = 20)
#	html_text = resp.read()
	soup = BeautifulSoup(html_text, 'lxml')
#	qlist = soup.findAll('h2', {'class':'question-item-title'})
	qlist = soup.findAll('div', {'class':'feed-main'})
	for q in qlist:
		s = list(q.find('h2').strings)
		link = q.find('a').get('href')
		print s[1] + '  time_num: ' + str(change_time(s[1]))  + '  ' + s[3]	+ 'link:' + link
		print type(link)

#	ok = False
#	while ok == False:
#		#todo post

def visit_question_page(url):
	resp = urllib2.urlopen(url, timeout = 20)
	html_text = resp.read()
	soup = BeautifulSoup(html_text, 'lxml')
	title_node = soup.find('h1', {'class':'QuestionHeader-title'})

	follow_status_node = soup.find('div', {'class':'QuestionFollowStatus'})
	
	answer_node = soup.find('h4', {'class':'List-headerText'})

	follow = list(follow_status_node.strings)
	answer = list(answer_node.strings)
	print '%s 关注:%s; 浏览:%s; 回答数:%s' %(title_node.text, follow[1], follow[3], answer[0].split(' ')[0])


if __name__ == '__main__':
	visit_question_page('https://www.zhihu.com/question/27325912')
#	test_question('https://www.zhihu.com/topic/19550429/newest', 120)