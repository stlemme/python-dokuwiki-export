
from . import DokuWiki
from . import dokuwikixmlrpc
import logging


class DokuWikiRemote(DokuWiki):
	def __init__(self, url, user, passwd):
		DokuWiki.__init__(self, url)
		self.client = dokuwikixmlrpc.DokuWikiClient(url, user, passwd)
		self.page_cache = {}

	def getpage(self, page, ns = [], pagens = None):
		fullname = self.resolve(page, ns)
		if pagens is not None:
			pagens[:] = fullname.split(self.ns_delimiter)[1:-1]
		if fullname in self.page_cache:
			return self.page_cache[fullname]
		logging.debug("Request page ")
		content = self.client.page(fullname[1:])
		# check if page does not exist
		if len(content) > 0:
			lines = content.split('\n')
		else:
			lines = None
		self.page_cache[fullname] = lines
		return lines

	def putpage(self, lines, page, ns = [], summary='regenerated'):
		content = '\n'.join(lines)
		fullname = self.resolve(page, ns)
		try:
			return self.client.put_page(fullname, content, summary=summary, minor=False)
		except dokuwikixmlrpc.DokuWikiXMLRPCError as dwerr:
			print(dwerr)
			print(page, fullname)
			return False

	def pageinfo(self, page, ns = []):
		fullname = self.resolve(page, ns)
		try:
			return self.client.page_info(fullname[1:])
		except dokuwikixmlrpc.DokuWikiXMLRPCError:
			return None
		
	def lockpage(self, page, ns = []):
		fullname = self.resolve(page, ns)
		return self.client.set_locks({'lock': [fullname]})
		
	def getfile(self, file, ns = []):
		fullname = self.resolve(file, ns)
		# res1 = self.client.file_info(fullname)
		try:
			res2 = self.client.get_file(fullname)
			# print(res1, len(res2))
			return res2
		except dokuwikixmlrpc.DokuWikiXMLRPCError as dwerr:
			print(dwerr)
			print(file, fullname)
		return None

	def putfile(self, file, data, ns = [], summary='updated'):
		fullname = self.resolve(file, ns)
		try:
			# print("save file: %s!" % fullname)
			return self.client.put_file(fullname, data, overwrite = True)
		except dokuwikixmlrpc.DokuWikiXMLRPCError as dwerr:
			print(dwerr)
			print(file, fullname)
			return False

	def fileinfo(self, file, ns = []):
		fullname = self.resolve(file, ns)
		try:
			info = self.client.file_info(fullname[1:])
			return info if info['size'] > 0 else None
		except dokuwikixmlrpc.DokuWikiXMLRPCError:
			return None

	def allpages(self):
		return self.client.all_pages()
		
	def searchpages(self, query):
		return self.client.search(query)
