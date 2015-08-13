
from . import SpecificEnabler


class DeprecatedSpecificEnabler(SpecificEnabler):
	def __init__(self, identifier, se_meta_page, originator):
		SpecificEnabler.__init__(self, identifier, se_meta_page, originator)
		self.set('/status', 'deprecated')
	
	@staticmethod
	def load(dw, identifier, se_meta_page, originator, licenses, partners, pub):
		se = DeprecatedSpecificEnabler(identifier, se_meta_page, originator)
		se.initialize(dw, licenses, partners, pub)
		return se
	