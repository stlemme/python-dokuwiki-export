
from .job import Job
from importlib import import_module
import logging


class JobFactory(object):
	def __init__(self):
		self.jobs = {}
		pass

	def load_job(self, jtype):
		if jtype in self.jobs:
			return self.jobs[jtype]

		impmod = import_module("." + jtype.lower(), package="jobs")
		if impmod is None:
			return None

		impclass = getattr(impmod, jtype, None)
		self.jobs[jtype] = impclass
		
		return impclass
		
	def create_job(self, jtype, params):
		try:
			jclass = self.load_job(jtype)
			job = jclass(**params)
		except Exception as e:
			logging.error("Unable to create job instance - exception occurred!\n%s" % e)
			job = None
		
		return job
