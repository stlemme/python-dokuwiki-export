
from . import Visitor


class InvalidEntitiesVisitor(Visitor):
	def __init__(self, keyword = None):
		Visitor.__init__(self)
		self.result = []
		self.keyword = keyword
		
	def visit_InvalidEntity(self, invalid):
		if self.keyword is not None:
			if invalid.get_keyword() != self.keyword:
				return
		
		self.result.append(invalid)

	def visit_SpecificEnabler(self, se):
		if se.is_valid():
			return
		self.result.append(se)

	def visit_DeprecatedSpecificEnabler(self, se):
		self.visit_SpecificEnabler(se)
		
	def get_result(self):
		return self.result

