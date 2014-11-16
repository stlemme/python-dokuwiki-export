
from . import GenericEnabler, SpecificEnabler, Application


class PrettyPrinter(object):
	def __init__(self):
		pass
	
	def dispatch(self, entity):
		methodname = 'print_' + entity.__class__.__name__
		method = getattr(self, methodname, self.print_generic)
		return method(entity)
		
	def print_GenericEnabler(self, entity):
		return '%s GE' % entity.get_name()

	def print_SpecificEnabler(self, entity):
		return '%s SE' % entity.get_name()
	
	def print_Application(self, entity):
		return entity.get_name()

	def print_Scenario(self, entity):
		return entity.get_name()

	def print_generic(self, entity):
		return str(entity)

