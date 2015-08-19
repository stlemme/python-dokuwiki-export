
from . import Wiki
import logging


class DokuWiki(Wiki):
	def __init__(self, url):
		Wiki.__init__(self, url)
		self.pagepath = '/doku.php/'
		self.filepath = '/lib/exe/fetch.php/'

	def pageurl(self, page, ns = [], heading = None):
		fullname = self.resolve(page, ns)
		if fullname is None:
			return None
		url = self.url + self.pagepath + fullname[1:]
		if heading is not None:
			url += '#' + self.target(heading)
		return url

	def fileurl(self, file, ns = []):
		fullname = self.resolve(file, ns)
		if fullname is None:
			return None
		url = self.url + self.filepath + fullname[1:]
		return url

	def resolve(self, page, rel_ns = [], pagens = None):
		if page is None:
			return None
		parts = page.split(self.ns_delimiter)

		# a page in the same namespace
		if len(parts) == 1:
			return self.ns_delimiter + self.ns_delimiter.join([self.cleanid(id).lower() for id in rel_ns + [page]]);
		
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
		
		
	def getsection(self, page, section, ns = [], pagens = None, targetlevel = 1):
		fullname = self.resolve(page, ns)
		if pagens is not None:
			pagens[:] = fullname.split(self.ns_delimiter)[1:-1]
		content = self.client.page(fullname[1:])
		lines = content.split('\n')
		
		seclines = []
		
		seclevel = None
		heading = None
		level = None
		
		for l in lines:
			heading_found = self.rx_heading.match(l)
			if heading_found is not None:
				heading, level = self.parseheading(heading_found.group())
				if heading == section:
					# found section, store section level
					# print('Found section "%s" - level:' % heading, level)
					seclevel = level
					continue
				
				if seclevel is not None:
					# print('Collecting section', seclevel, level)
					if seclevel >= level:
						# print('Found next section "%s" - level:' % heading, level)
						# found same level or above heading after section
						break
			
			if seclevel is None:
				continue

			# re-adjust heading level
			if heading_found is not None:
				# print("Found heading - ", level, seclevel, targetlevel, heading)
				l = self.heading(targetlevel + level - seclevel, heading)

			seclines.append(l)
			
		if len(seclines):
			return seclines

		return None
