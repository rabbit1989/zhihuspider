#coding=utf-8
import threading
import utils
import logging
import ConfigParser

class TaskManager:
	def __init__(self):
		self.workers = None
		self.task_name = None
		self.data = None
		self.result = None
		self.cf = ConfigParser.ConfigParser()
		self.cf.read('config.ini')

	def add_workers(self, workers):
		self.workers = workers

	def set_task(self, task_name, data):
		self.task_name = task_name
		self.data = data

	def run(self):
		'''
			do_task 是阻塞的，task完成之后才会返回
		'''
		logging.info('TaskManager: run task %s', self.task_name)
		num_worker = len(self.workers)
		data_slices = utils.split_data(self.data, num_worker)
		
		if self.cf.get('general', 'tiny_test') == '1':
			logging.info('TaskManager: -------------------run tiny_test-----------------------')
			for i in xrange(len(data_slices)):
				data_slices[i] = utils.select_subset(data_slices[i], 2)

		threads = []
		for i in xrange(num_worker):
			threads.append(threading.Thread(target = getattr(self.workers[i], self.task_name), args=(data_slices[i],)))
			threads[i].start()
		
		for i in xrange(num_worker):
			threads[i].join()

		self.result = utils.merge_data([worker.rst for worker in self.workers])

	def get_result(self):
		return self.result