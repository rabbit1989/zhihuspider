#coding=utf-8
import urllib2
import re
from bs4 import BeautifulSoup


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
		print s[1] + '  time_num: ' + str(change_time(s[1]))  + '  ' + s[3]	+ 'link:' + q.find('a').get('href')

#	ok = False
#	while ok == False:
#		#todo post


if __name__ == '__main__':
	pass
#	test_question('https://www.zhihu.com/topic/19550429/newest', 120)