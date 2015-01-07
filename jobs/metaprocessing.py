
from . import Job
import metagenerate
import logging


class MetaProcessing(Job):
	def __init__(self, metapage, outpage):
		Job.__init__(self)
		self.metapage = metapage
		self.outpage = outpage
	
	def summary(self):
		return "Regenerating output from meta structure at %s" % self.outpage
	
	def required(self):
		return True

	def perform(self, fidoc):
		metagenerate.generate_meta_information(fidoc, self.outpage)
		return True

	def responsible(self, fidoc):
		# TODO: retrieve last author of metapage
		dw = fidoc.get_wiki()
		info = dw.pageinfo(self.metapage)
		return info['author']

