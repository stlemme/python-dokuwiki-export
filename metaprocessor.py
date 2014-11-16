
from metagrammar import *
import logging


# TODO: refactor as internal class
class MetaAdapter(object):
	def __init__(self, partners):
		self.partners = partners
		self.ids = set()
		self.entities = {}
		
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
	def __init__(self, adapter):
		self.adapter = adapter
	
	def process(self, metadoc):
		
		p = MetaStructureGrammar.parser(self.adapter)

		try:
			result = p.parse_text(metadoc, reset=True, bol=True, eof=True)
				
			if len(p.remainder()):
				logging.error("Unable to parse: %s ..." % p.remainder()[:60])
				return None
				
			# print()
			# print(p.remainder())
			
			return result

		except (ParseError, MetaError) as e:
			logging.error('Parsing failed!')
			logging.error(str(e))
			return None
		pass

