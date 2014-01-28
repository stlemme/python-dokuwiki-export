
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
		
	def getsection(self, page, section, ns = [], pagens = None):
		return None

	def putpage(self, lines, page, ns = [], summary='regenerated'):
		pass

	def pageurl(self, page, ns = [], heading = None):
		return None
		
	def pageinfo(self, page, ns = []):
		return None
		
	def getfile(self, file, ns = []):
		return None

	def allpages(self):
		return None
		
	rx_heading = re.compile(r"^(=+) ([^=]+) (=+)$")

	def parseheading(self, heading):
		result = self.rx_heading.match(heading)
		if result is None:
			return None, None
			
		indent1 = len(result.group(1))
		indent2 = len(result.group(3))
		if indent1 != indent2:
			logging.warning("Warning! Invalid heading.")
				
		level = 7 - indent1
		return result.group(2), level
	
	def heading(self, level, heading):
		return ("=" * (7 - level)) + " " + heading + " " + ("=" * (7 - level)) + "\n"

	
	rx_link = re.compile(r"\[\[([^\|\]]+)(\|([^\]]+))?\]\]")

	def parselink(self, link):
		result = self.rx_link.match(link)
		# print result.groups()
		target = result.group(1)
		parts = target.split('#', 1)
		page = parts[0]
		section = parts[1] if len(parts) > 1 else None
		text = result.group(3)
		return page, section, text
		
	def link(self, page, section, text):
		link = '[[' + page
		if section is not None:
			link += '#' + section
		if text is not None:
			link += '|' + text
		link += ']]'
		return link
	
	# def target(self, heading):
		# target = heading.replace(' ', '_')
		# target = re.sub('[\W]+', '', target).lower()
		# print(target)
		# return target

	def cleanid(self, id):
		sepcharpat = '\\' + self.sep + '+';

		# //remove specials
		target = re.sub('[^\w:\+\._\-]+', self.sep, id)
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
		
		return target
	
	def target(self, heading):
		# print(heading)
		target = heading.strip().lower();

		# //alternative namespace seperator
		target = target.replace(';', ':')
		if self.useslash:
			target = target.replace('/', ':')
		else:
			target = target.replace('/', self.sep)

		target = self.cleanid(target)

		target = re.sub('[:\.]+', '', target)
		new = target.lstrip('0123456789_-')
		# print(7, target)
		# print(8, new)

		return new if len(new) else 'section' + re.sub('[^0-9]+', '' , target)

		
	rx_include = re.compile(r"{{page>([^}#]+)(#([^}]+))?}}")
	
	def parseinclude(self, include):
		result = wiki.rx_include.match(include)
		if result is None:
			return None, None
		incpage = result.group(1)
		incsection = result.group(3)
		return incpage, incsection
		
		
	rx_image = re.compile(r"{{( *)([^\?\|\} ]+)(\?([^\|\} ]+))?( *)(\|([^\}]*))?}}")
	rx_imageresize = re.compile(r"^([0-9]+)(x([0-9]+))?$")

	def parseimage(self, image):
		result = self.rx_image.match(image)
		if result is None:
			return None, None, None

		file  = result.group(2)
		filll = len(result.group(1)) > 0
		fillr = len(result.group(5)) > 0
		caption = result.group(7)
		params = {}
		
		# resizing
		if result.group(4) is not None:
			imgparams = result.group(4).split('&')
		
			for p in imgparams:
				if p == 'nolink':
					params['nolink'] = True
					continue
					
				result = self.rx_imageresize.match(p)
				if result is None:
					continue
					
				# print result.groups()
				params['width'] = int(result.group(1))
				if result.group(3) is not None:
					params['height'] = int(result.group(3))
					
		# alignment
		if filll:
			params['jc'] = 'right'
		elif fillr:
			params['jc'] = 'left'
		if filll and fillr:
			params['jc'] = 'center'

		return file, caption, params
	
	
	def image(self, file, caption, params):
		image = '{{'
		if 'jc' in params:
			if params['jc'] != 'left':
				image += '  '
		image += file
		if params is not None:
			s = []
			if 'width' in params:
				imagesize = params['width']
				if 'height' in params:
					imagesize += 'x' + params['height']
				s.append(imagesize)
			if 'nolink' in params:
				if params['nolink']:
					s.append('nolink')
			if len(s):
				image += '?' + '&'.join(s)
		if 'jc' in params:
			if params['jc'] != 'right':
				image += '  '
		if caption is not None:
			image += '|' + caption
		image += '}}'
		return image
		

	

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

	def resolve(self, page, rel_ns = [], pagens = None):
		parts = page.split(self.ns_delimiter)

		# a page in the same namespace
		if len(parts) == 1:
			return self.ns_delimiter + self.ns_delimiter.join(rel_ns + [page]).lower();
		
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
		
		if pagens is not None:
			pagens[:] = path[:-1]
			
		return self.ns_delimiter + self.ns_delimiter.join([self.cleanid(id).lower() for id in path])
		
	def resolverel(self, page, ns):
		parts = page.split(self.ns_delimiter)
		path = parts[1:]
		
		trail = 0
		for i, p in enumerate(ns):
			if p != path[i]:
				break
			trail += 1
		
		rel_path = ['..'] * len(ns[trail:])
		if len(rel_path) >= trail:
			return page
		
		path = path[trail:]
		
		if len(rel_path) == 0 and len(path) > 1:
			rel_path = ['.']
		
		path = rel_path + path
		
		return self.ns_delimiter.join(path)
		
		
	def getsection(self, page, section, ns = [], pagens = None):
		fullname = self.resolve(page, ns)
		if pagens is not None:
			pagens[:] = fullname.split(self.ns_delimiter)[1:-1]
		content = self.client.page(fullname[1:])
		lines = content.split('\n')
		
		seclines = []
		
		for l in lines:
			result = self.rx_heading.match(l)
			if result is not None:
				heading, level = self.parseheading(result.group())
				skip = heading != section
				continue
			
			if skip:
				continue

			seclines.append(l)

		return seclines


from . import dokuwikixmlrpc

class DokuWikiRemote(DokuWiki):
	def __init__(self, url, user, passwd):
		DokuWiki.__init__(self, url)
		self.client = dokuwikixmlrpc.DokuWikiClient(url, user, passwd)

	def getpage(self, page, ns = [], pagens = None):
		fullname = self.resolve(page, ns)
		if pagens is not None:
			pagens[:] = fullname.split(self.ns_delimiter)[1:-1]
		content = self.client.page(fullname[1:])
		lines = content.split('\n')
		return lines

	def putpage(self, lines, page, ns = [], summary='regenerated'):
		content = '\n'.join(lines)
		fullname = self.resolve(page, ns)
		try:
			self.client.put_page(fullname, content, summary=summary, minor=False)
		except dokuwikixmlrpc.DokuWikiXMLRPCError as dwerr:
			print(dwerr)
			print(page, fullname)

	def pageinfo(self, page, ns = []):
		fullname = self.resolve(page, ns)
		return self.client.page_info(fullname[1:])
		
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

	def allpages(self):
		return self.client.all_pages()


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
