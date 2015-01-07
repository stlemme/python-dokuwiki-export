
from . import Job
from cataloggenerate import generate_catalog
import logging


class UpdateCatalog(Job):
	def __init__(self, template_filename = None, responsible = None):
		Job.__init__(self)
		self.template_filename = template_filename
		self.responsible = responsible
	
	def summary(self):
		return "Updating catalog with template file %s" % self.template_filename
	
	def required(self):
		return True

	def perform(self, fidoc):
		generate_catalog(fidoc, self.template_filename)
		logging.info("Finished!")
		return True
		
	def responsible(self, fidoc):
		return self.responsible

