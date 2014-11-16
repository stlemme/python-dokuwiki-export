
from . import NamedEntity
	
	
class InvalidEntity(NamedEntity):
	def __init__(self, keyword, name):
		NamedEntity.__init__(self, name)
		self.keyword = keyword
	
	def get_keyword(self):
		return self.keyword
		
	def __repr__(self):
		return "InvalidEntity<%s %s>" % (self.keyword, self.get_name())
