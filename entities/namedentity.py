
from . import Entity


class NamedEntity(Entity):
	def __init__(self, name):
		Entity.__init__(self)
		self.name = name
		
	def get_name(self):
		return self.name
	
	def __repr__(self):
		return "%s<%s>" % (self.__class__.__name__, self.get_name())
