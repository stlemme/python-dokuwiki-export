
from . import NamedEntity


class Application(NamedEntity):
	def __init__(self, name, provider):
		NamedEntity.__init__(self, name)
		self.provider = provider
	
	def get_descendants(self):
		return []
