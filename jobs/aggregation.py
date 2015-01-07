
from . import Job
from aggregate import *
import logging


class Aggregation(Job):
	def __init__(self, tocpage, outpage, editor = None, embedwikilinks = True):
		Job.__init__(self)
		self.tocpage = tocpage
		self.outpage = outpage
		self.embedwikilinks = embedwikilinks
		self.editor = editor
	
	def summary(self):
		return "Aggregating %s" % self.tocpage
	
	def required(self):
		return True

	def perform(self, fidoc):
		dw = fidoc.get_wiki()
		logging.info("Loading table of contents %s ..." % self.tocpage)
		tocns = []
		toc = dw.getpage(self.tocpage, pagens = tocns)
		if toc is None:
			logging.error("Table of contents %s not found." % self.tocpage)
			return False
			
		logging.info("Aggregating pages ...")
		doc, chapters = aggregate(dw, toc, tocns, self.embedwikilinks)

		logging.info("Flushing generated content to page %s ..." % self.outpage)
		res = dw.putpage(doc, self.outpage)
		# print(res)
		# locks = dw.lockpage(self.outpage)
		# logging.info("Locks: %s" % locks)
		return res
		
	def responsible(self, fidoc):
		return self.editor

