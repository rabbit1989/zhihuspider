#coding=utf-8
import sys
import common.db as db
import logging
import ConfigParser
import time
#import crawl_rule
import traceback
import os
import cPickle
import gc
import common.utils
import re
import requests
import json
import urllib2
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

class logic_base:
	def __init__(self):
		self.proxy = {}

	def assign_works(self, ):
		'''
			called by crawl master
		'''
		pass

	def receive_work_result(self, result):
		'''
			called by crawl master
		'''		
		pass

	def on_assign_works(self, _input):
		'''
			called by crawl slave
		'''
		pass

	def prepare_work(self, ):
		'''
			called by crawl master
		'''
		pass

	def set_proxy(self, proxy):
		self.proxy = proxy
