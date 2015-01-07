
from . import Job
import actionitems
import logging


class UpdateActionItems(Job):
	def __init__(self, outpage, namespace = ':ficontent:', exceptions = []):
		Job.__init__(self)
		self.outpage = outpage
		self.namespace = namespace
		self.exceptions = exceptions
	
	def summary(self):
		return "Updating action items of namespace %s" % self.namespace
	
	def required(self):
		return True

	def perform(self, fidoc):
		dw = fidoc.get_wiki()
		actionitems.updateactionitems(dw, self.outpage, self.namespace, self.exceptions)
		return True

	def responsible(self, fidoc):
		return 'DFKI-Stefan'

