
from metagrammar import *


# TODO: rename to MetaAdapter
class MetaData(object):
	def __init__(self, partners, warning = print, error = print):
		self.partners = partners
		self.ids = set()
		self.entities = {}
		
		self.warning = warning
		self.error = error
		
	def add_id(self, id):
		if id in self.ids:
			return True
		self.ids.add(id)
		return False
	
	def map(self, stmt, entity):
		self.entities[stmt.get_identifier()] = entity
		for id in stmt.get_aliases():
			self.entities[id] = entity
		
	def find(self, id):
		return self.entities[id] if id in self.entities else None
	
		

class MetaProcessor:
	def __init__(self, data):
		self.data = data
	
	def process(self, metadoc):
		
		p = MetaStructureGrammar.parser(self.data)

		try:
			result = p.parse_text(metadoc, reset=True, bol=True, eof=True)
				
			if len(p.remainder()):
				self.data.error("Unable to parse: %s ..." % p.remainder()[:60])
				return None
				
			# print()
			# print(p.remainder())
			
			return result

		except (ParseError, MetaError) as e:
			self.data.error('Parsing failed!')
			self.data.error(str(e))
			return None
		pass

