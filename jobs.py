
from aggregate import *
import sys
import wikiconfig
import logging
import datetime
from outbuffer import PageBuffer


class Job(object):
	def __init__(self):
		pass
		
	def summary(self):
		return "Unknown Job"

	def perform(self, dw):
		return False
		

class Aggregation(Job):
	def __init__(self, tocpage, outpage, embedwikilinks = True):
		Job.__init__(self)
		self.tocpage = tocpage
		self.outpage = outpage
		self.embedwikilinks = embedwikilinks
		
	def summary(self):
		return "Aggregating %s" % self.tocpage

	def perform(self, dw):
		logging.info("Loading table of contents %s ..." % self.tocpage)
		tocns = []
		toc = dw.getpage(self.tocpage, pagens = tocns)
		if toc is None:
			logging.error("Table of contents %s not found." % self.tocpage)
			return False
			
		logging.info("Aggregating pages ...")
		doc, chapters = aggregate(dw, toc, tocns, self.embedwikilinks)

		logging.info("Flushing generated content to page %s ..." % self.outpage)
		dw.putpage(doc, self.outpage)
		return True


jobs = [
	Aggregation(":ficontent:private:deliverables:d65:toc", ":ficontent:private:deliverables:d65:"),
	Aggregation(":ficontent:private:deliverables:d42:toc", ":ficontent:private:deliverables:d42:")
]

jobslog = ":ficontent:private:wikijobs.log"

class PageLog(PageBuffer):
	def __init__(self, wiki, page):
		PageBuffer.__init__(self, wiki, page)
		self.current = ""

	def write(self, text):
		lines = text.split('\n')
		self.current += lines[0]
		if len(lines) == 1:
			return
		
		for l in lines[1:-1]:
			PageBuffer.write(self, l)
		
		PageBuffer.write(self, self.current)
		self.current = lines[-1]
	
	def flush(self):
		PageBuffer.write(self, self.current)
		self.current = ""
		PageBuffer.flush(self)


if __name__ == "__main__":
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	log = PageLog(dw, jobslog)
	logging.out = log
	
	log << dw.heading(1, "Log of dokuwikibot's jobs")
	log << ""
	log << "Latest run at %s" % datetime.datetime.now()
	log << ""
	log << "<code>"

	logging.info("Connected to remote DokuWiki at %s" % wikiconfig.url)

	for i, j in enumerate(jobs):
		logging.info("JOB %d of %d: %s" % (i+1, len(jobs), j.summary()))
		j.perform(dw)

	logging.info("All done.")

	log << ""
	log << "</code>"
	log << ""

	log.flush()
