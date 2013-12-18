
from metagrammar import *

class MetaData(object):
	def __init__(self, warning = print, error = print):
		self.ge = {}
		self.se = {}
		self.loc = {}
		self.app = {}
		
		self.warning = warning
		self.error = error

	def enabler(self, id):
		if id in self.ge:
			return self.ge[id]
		if id in self.se:
			return self.se[id]
		return None

class metaprocessor:
	def __init__(self, data = MetaData()):
		self.data = data
	
	def process(self, doc):
		meta = '\n'.join(doc)
		
		p = MyGrammar.parser(self.data)
		try:
			result = p.parse_text(meta, reset=True, bol=True, eof=True)
				
			if len(p.remainder()):
				error("Unable to parse: %s ..." % p.remainder()[:60])
				# return None
				
			print()
			# print(p.remainder())
			
			return result

		except (ParseError, MetaError) as e:
			print('Parsing failed!')
			print(e)
			return None
		pass
