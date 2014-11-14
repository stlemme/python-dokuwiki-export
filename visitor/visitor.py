
class Visitor(object):
		
	def get_result(self):
		return None
	
	def visit(self, entity):
		self.internal_visit(entity)
	
	def internal_visit(self, entity):
		method = 'visit_' + entity.__class__.__name__
		visit = getattr(self, method, self.generic_visit)
		return visit(entity)

	def generic_visit(self, entity):
		for e in entity.get_descendants():
			self.internal_visit(e)
