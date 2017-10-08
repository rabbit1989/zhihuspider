#coding=utf-8
import sys
import MySQLdb
import ConfigParser
import logging

class DBConnection:
	def __init__(self, cf):
		self.host = cf.get("db", "host")
		self.port = int(cf.get("db", "port"))
		self.user = cf.get("db", "user")
		self.passwd = cf.get("db", "passwd")
		self.db_name = cf.get("db", "db")
		self.charset = cf.get("db", "charset")
		self.use_unicode = cf.get("db", "use_unicode")
		self.connect()
		
	def connect(self):
		logging.info('connect db %s', self.db_name)
		self.db = MySQLdb.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd, db=self.db_name, charset=self.charset, use_unicode=self.use_unicode)
		self.cursor = self.db.cursor()


	def execute(self, sql, param_list = None):
		if param_list is not None and len(param_list) >= 1:
			self.cursor.executemany(sql, param_list)
		else:
			self.cursor.execute(sql)
	def fetch_results(self):
		return self.cursor.fetchall()
		
	def close(self):
		self.db.close()

	def process_exception(self, error):
		logging.fatal(error)
		#出异常就重连一下
		self.connect()
