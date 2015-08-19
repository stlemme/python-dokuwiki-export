
from . import DokuWiki
import logging


class DokuWikiLocal(DokuWiki):
	def __init__(self, url, pages, media):
		DokuWiki.__init__(self, url)
		self.pages = pages
		self.media = media

	def getpage(self, page, ns = [], pagens = None):
		# this could be replaced to utilize the dokuwiki xml-rpc
		fullname = self.resolve(page, ns)
		filename = fullname.replace(self.ns_delimiter, '/').lower()
		# print 'getpage(%s, %s) => %s - %s' % (page, ns, fullname, filename)
		return self.readfile(self.pages + filename + ".txt")
	
	def readfile(self, filename):
		try:
			fo = open(filename, "r")
			content = fo.readlines()
			fo.close()
		except IOError:
			content = None
		return content
