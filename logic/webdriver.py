#coding=utf-8
from selenium import webdriver
import ConfigParser
import logging
import time

class WebDriver:
	def __init__(self):
	#	chrome_options = webdriver.ChromeOptions()
	#	chrome_options.add_argument('--proxy-server=http://119.90.63.3:3128')
	#	self.driver = webdriver.Chrome()
		self.driver = None

	def login(self):
		cf = ConfigParser.ConfigParser()
		cf.read('config.ini')
		success = False
		while success == False:
			#直到登录成功才返回，有可能浏览器被劫持了，第一次没有访问到指定页面 
			try:
				self.get_page('http://www.zhihu.com')
				self.driver.find_element_by_link_text('登录').click()
				self.driver.find_element_by_class_name('signin-switch-password').click()
				self.driver.find_element_by_name('account').send_keys(cf.get('login', 'account'))
				#密码，这里要替换为你的密码
				self.driver.find_element_by_name('password').send_keys(cf.get('login', 'password'))
				success = True
			except Exception, e:
				logging.fatal(e)

	def get_page(self, url, scroll_end = False):
		if self.driver is None:
			self.driver = webdriver.Chrome()				
		self.driver.get(url)
		if scroll_end == True:
			while True:
				try:
				#	self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
					time.sleep(.25)
					ele = self.driver.find_elements_by_class_name('zg-btn-white')
					if len(ele) <= 1:
						break
					else:
						ele[0].click()
				except Exception, e:
					logging.fatal(e)

	def page_source(self):
		return self.driver.page_source		
