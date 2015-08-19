
import re
import string
import logging


class Wiki(object):
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
		
	def pageexists(self, page, ns = []):
		info = self.pageinfo(page, ns)
		return info is not None
	
	def getfile(self, file, ns = []):
		return None
		
	def putfile(self, file, data, ns = [], summary='updated'):
		pass

	def fileurl(self, file, ns = []):
		return None

	def fileinfo(self, file, ns = []):
		return None

	def allpages(self):
		return None
		
	def search(self, query):
		return None
		
	rx_heading = re.compile(r"^(=+) ([^=]+) (=+)\s*$")

	def parseheading(self, heading):
		result = self.rx_heading.match(heading)
		if result is None:
			return None, None
		
		indent1 = len(result.group(1))
		indent2 = len(result.group(3))
		if indent1 != indent2:
			logging.warning("Invalid heading.\n\"%s\"" % heading)
		
		level = 7 - indent1
		return result.group(2), level
	
	def heading(self, level, heading):
		if level < 1:
			logging.warning('Invalid level of %s for heading "%s"' % (level, heading))
		return ("=" * (7 - level)) + " " + heading + " " + ("=" * (7 - level))


	rx_link = re.compile(r"\[\[([^\|]+?)(\|(.+?))?\]\]")

	def parselink(self, link):
		result = self.rx_link.match(link)
		# print result.groups()
		if result is None:
			return None, None, None
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
		result = self.rx_include.match(include)
		if result is None:
			return None, None
		incpage = result.group(1)
		incsection = result.group(3)
		return incpage, incsection
	
	def include(self, page, section):
		include = '{{page>' + page
		if section is not None:
			include += '#' + section
		include += '}}'
		return include
		
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
				imagesize = str(params['width'])
				if 'height' in params:
					imagesize += 'x' + str(params['height'])
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
