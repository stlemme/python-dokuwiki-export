
from . import Visitor


class MetaVisitor(Visitor):
	def visit(self, entity):
		self.stack = [entity]
		
		while len(self.stack):
			entity = self.stack.pop()
			next = self.internal_visit(entity)
			if next is not None:
				self.stack.extend(next)
	
	def internal_visit(self, entity):
		method = 'visit_' + entity.__class__.__name__
		visit = getattr(self, method, self.generic_visit)
		return visit(entity)

	def generic_visit(self, entity):
		pass

