
import re
import string


class wiki(object):
	def __init__(self, url):
		self.url = url
		self.ns_delimiter = ":"
		self.default_ns_page = "start"
		self.useslash = False
		self.sep = '_'

	def getpage(self, page, ns = [], pagens = None):
		return None

	def putpage(self, lines, page, ns = []):
		pass

	def pageurl(self, page, ns = [], target = None):
		return None
		
	
	rx_heading = re.compile(r"^(=+) ([^=]+) (=+)$")

	def heading(self, level, heading):
		return ("=" * (7 - level)) + " " + heading + " " + ("=" * (7 - level)) + "\n"

	
	rx_link = re.compile(r"^\[\[([^\|\]]+)(\|([^\]]+))?\]\]$")

	def parselink(self, link):
		result = self.rx_link.match(link)
		# print result.groups()
		target = result.group(1)
		text = result.group(3)
		return target, text
		
	# def target(self, heading):
		# target = heading.replace(' ', '_')
		# target = re.sub('[\W]+', '', target).lower()
		# print(target)
		# return target

	def target(self, heading):
		sepcharpat = '\\' + self.sep + '+';
		# print(heading)
		target = heading.strip().lower();

		# //alternative namespace seperator
		target = target.replace(';', ':')
		if self.useslash:
			target = target.replace('/', ':')
		else:
			target = target.replace('/', self.sep)

		# //remove specials
		target = re.sub('[^\w:\+\._\-]+', self.sep, target)
		# print(1, target)

		# //clean up
		target = re.sub(sepcharpat, self.sep, target)
		# print(2, target)
		target = re.sub(':+', ':', target)
		# print(3, target)
		target = target.strip(':._-')
		# print(4, target)
		target = re.sub(':[:\._\-]+', ':', target)
		# print(5, target)
		target = re.sub('[:\._\-]+:', ':', target)
		# print(6, target)
		
		target = re.sub('[:\.]+', '', target)
		new = target.lstrip('0123456789_-')
		# print(7, target)
		# print(8, new)

		return new if len(new) else 'section' + re.sub('[^0-9]+', '' , target)


class DokuWiki(wiki):
	def __init__(self, url):
		wiki.__init__(self, url)
		self.pagepath = '/doku.php/'

	def pageurl(self, page, ns = [], heading = None):
		fullname = self.resolve(page, ns)
		url = self.url + self.pagepath + fullname[1:]
		if heading is not None:
			url += '#' + self.target(heading)
		return url
	
	def resolve(self, page, rel_ns = []):
		parts = page.split(self.ns_delimiter)

		# a page in the same namespace
		if len(parts) == 1:
			return self.ns_delimiter + self.ns_delimiter.join(rel_ns + [page]);
		
		# referring to a namespace rather than a page
		if len(parts[-1]) == 0:
			parts[-1] = self.default_ns_page

		# referring to global namespace
		if len(parts[0]) == 0:
			path = []
			parts = parts[1:]
		else:
			path = rel_ns[:]
		
		trail = 0
		for ns in parts[:-1]:
			if ns == '..':
				#parent
				trail += 1
				path.pop()
			elif ns == '.':
				#current
				trail += 1
			else:
				break
		
		path = path + parts[trail:]
		return self.ns_delimiter + self.ns_delimiter.join(path)
		
		

from . import dokuwikixmlrpc

class DokuWikiRemote(DokuWiki):
	def __init__(self, url, user, passwd):
		DokuWiki.__init__(self, url)
		self.client = dokuwikixmlrpc.DokuWikiClient(url, user, passwd)

	def getpage(self, page, ns = [], pagens = None):
		# this could be replaced to utilize the dokuwiki xml-rpc
		fullname = self.resolve(page, ns)
		if pagens is not None:
			pagens[:] = fullname.split(self.ns_delimiter)[1:-1]
			# print(pagens)
		# filename = fullname.replace(self.ns_delimiter, '/').lower()
		# print('getpage(%s, %s) => %s' % (page, ns, fullname))
		content = self.client.page(fullname[1:])
		lines = content.split('\n')
		return lines

	def putpage(self, lines, page, ns = []):
		content = '\n'.join(lines)
		fullname = self.resolve(page, ns)
		self.client.put_page(fullname, content, summary='regenerated', minor=False)


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
