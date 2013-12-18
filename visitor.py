
class Visitor(object):
	def visit(self, grammar):
		method = 'visit_' + grammar.__class__.__name__
		visit = getattr(self, method, self.generic_visit)
		return visit(grammar)

	def generic_visit(self, grammar):
		for e in grammar.elements:
			if e is not None:
				self.visit(e)


class ExperimentsVisitor(Visitor):
	def __init__(self, site = None):
		self.result = []
		self.site = site
		
	def visit_EXPERIMENT(self, grammar):
		if self.site is not None:
			if grammar.site != self.site:
				return
		self.result.append(grammar)

