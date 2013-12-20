
class OutBuffer(object):
	def __lshift__(self, text):
		self.write(text)
		
	def write(self, text):
		pass

	def flush(self):
		pass


class PageBuffer(OutBuffer):
	def __init__(self, wiki, page):
		self.result = []
		self.wiki = wiki
		self.page = page
		
	def write(self, text):
		self.result.append(text)

	def flush(self):
		self.wiki.putpage(self.result, self.page)


class OutStreamBuffer(OutBuffer):
	def __init__(self, out):
		self.out = out
		
	def write(self, text):
		self.out.write(text)
		self.out.write('\n')


class FileBuffer(OutStreamBuffer):
	def __init__(self, filename):
		try:
			self.fo = open(filename, 'w')
			OutStreamBuffer.__init__(self, self.fo)
		except IOError:
			pass
		
	def flush(self):
		if self.fo is not None:
			self.fo.close()
		
