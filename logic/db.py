#coding=utf-8
import sys
import MySQLdb
import ConfigParser

class DBConnection:
	def __init__(self, cf):
		host = cf.get("db", "host")
		port = int(cf.get("db", "port"))
		user = cf.get("db", "user")
		passwd = cf.get("db", "passwd")
		db_name = cf.get("db", "db")
		charset = cf.get("db", "charset")
		use_unicode = cf.get("db", "use_unicode")
		self.db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=db_name, charset=charset, use_unicode=use_unicode)
		self.cursor = self.db.cursor()

	def execute(self, sql, param_list):
		if len(param_list) >= 1:
			self.cursor.executemany(sql, param_list)
		else:
			self.cursor.execute(sql)
	def fetch_results(self):
		return self.cursor.fetchall()
		
	def close(self):
		self.db.close()