
from wiki import *
from aggregate import *
import logging


class wikipublisher(object):

	def __init__(self, dw, export_ns = []):
		self.dw = dw
		self.export_ns = export_ns
	
	
	def public_page(self, page, rel_ns = []):
		fullname = self.dw.resolve(page, rel_ns)
		
		fullname = fullname.replace(':', '.').strip('.')
		
		if fullname.endswith(".start"):
			fullname = fullname[:-6]
		
		fullname = self.dw.resolve(fullname, self.export_ns)
		return fullname
	
	
	def public_file(self, file, rel_ns = []):
		return self.public_page(file, rel_ns)

		
	def publish(self, src, dest):
		srcns = []
		fullsrc = self.dw.resolve(src, [], srcns)
		# doc = self.dw.getpage(src, [], srcns)
		
		destns = []
		self.dw.resolve(dest, [], destns)

		toc = [
			'  - [[%s]]' % fullsrc
		]
		
		doc, chapters = aggregate(self.dw, toc, srcns)
		
		# print(len(doc))
		# print(chapters)
		
		newdoc = []
		
		for line in doc:
			re1line = wiki.rx_link.sub(lambda m: self.resolve_link(srcns, destns, m), line)
			re2line = wiki.rx_image.sub(lambda m: self.resolve_image(srcns, destns, m), re1line)
			newdoc.append(re2line)

		self.dw.putpage(newdoc, dest, summary='publish page')
	
	
	def resolve_link(self, srcns, destns, match):
		page, section, text = self.dw.parselink(match.group())

		if page.startswith('http'):
			return self.dw.link(page, section, text)

		oldns = []
		fullname = self.dw.resolve(page, srcns, oldns)
		mappedname = self.public_page(fullname)
		
		# print(page)
		# print(fullname)
		# print(oldns)
		# print(mappedname)
		# print(newname)
		
		# print("Resolve link %s -> %s" % (fullname, mappedname))
		
		# TODO: indicate private links
		if mappedname is not None:
			fullname = self.dw.resolverel(mappedname, destns)
		else:
			logging.warning("Unresolved link %s" % fullname)

		return self.dw.link(fullname, section, text)
		
		
	def resolve_image(self, srcns, destns, match):
		file, caption, params = self.dw.parseimage(match.group())
		# print(file, caption, params)
		# print("Image %s" % file)
		# return match.group()
		
		if file.startswith('http'):
			fullname = file
		else:
			fullname = self.dw.resolve(file, srcns)
		# print(fullname)

		logging.info("Image %s" % fullname)
		
		mappedname = self.public_file(fullname)
		# print("      %s" % mappedname)
		
		if mappedname is not None:
			srcinfo = self.dw.fileinfo(fullname)
			destinfo = self.dw.fileinfo(mappedname)
			
			# print(srcinfo)
			# print(destinfo)
			
			if (srcinfo['size'] != destinfo['size']) or (srcinfo['lastModified'] > destinfo['lastModified']):
				logging.info("Copy image ...")
				data = self.dw.getfile(fullname)
				if not self.dw.putfile(mappedname, data):
					logging.warning("Copy failed!")
			
			newname = self.dw.resolverel(mappedname, destns)
			
		else:
			logging.warning("Unresolved image %s" % fullname)
			newname = fullname
		
		image = self.dw.image(newname, caption, params)
		# print(image)
		return image


class restrictedwikipublisher(wikipublisher):

	def __init__(self, dw, public_pages, exceptions = [], export_ns = []):
		wikipublisher.__init__(self, dw, export_ns)
		self.public_pages = public_pages
		self.exceptions = exceptions

	
	def public_page(self, page, rel_ns = []):
		fullname = self.dw.resolve(page, rel_ns)
		
		public = False
		for rx in self.public_pages:
			if rx.match(fullname) is not None:
				public = True
				break
		
		if not public:
			return None
		
		for rx in self.exceptions:
			if rx.match(fullname) is not None:
				return None
		
		return wikipublisher.public_page(self, fullname)
	
