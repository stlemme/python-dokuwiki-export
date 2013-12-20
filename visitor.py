
class Visitor(object):
	def visit(self, grammar):
		self.internal_visit(grammar)
	
	def internal_visit(self, grammar):
		method = 'visit_' + grammar.__class__.__name__
		visit = getattr(self, method, self.generic_visit)
		return visit(grammar)

	def generic_visit(self, grammar):
		for e in grammar.elements:
			if e is not None:
				self.internal_visit(e)


class ExperimentsVisitor(Visitor):
	def __init__(self, site = None, scenario = None):
		self.result = []
		self.site = site
		self.scenario = scenario
		
	def visit_EXPERIMENT(self, grammar):
		if self.site is not None:
			if grammar.site != self.site:
				return
		if self.scenario is not None:
			if grammar.scenario != self.scenario:
				return
		self.result.append(grammar)


# class DependencyVisitor(Visitor):
	# def __init__(self, entity, relations = ['USES'], se = True, ge = True):
		# self.entity = entity
		# self.relations = relations
		# self.se = se
		# self.ge = ge
		# self.result = []
		
	# def visit_SE(self, grammar):
		# if grammar == self.entity:
			# return
			
		# for r in self.relations:
			# pass
		
class UsedByVisitor(Visitor):
	def __init__(self, enabler, relation = 'USES', se = True, app = True, experiment = True, transitive = False):
		self.result = []
		self.enabler = enabler
		self.relation = relation
		self.se = se
		self.app = app
		self.experiment = experiment
		self.transitive = transitive
		
	def visit_SE(self, grammar):
		if not self.se:
			return
			
		if grammar in self.result:
			return

		if self.enabler in grammar.usestates[self.relation]:
			self.result.append(grammar)
			return
		
		if not self.transitive:
			return
			
		for e in grammar.usestates[self.relation]:
			self.visit(e)
			if e in self.result:
				self.result.append(grammar)
				return
		
		
	def visit_APP(self, grammar):
		if not self.app:
			return
			
		if grammar in self.result:
			return

		if self.enabler in grammar.usestates[self.relation]:
			self.result.append(grammar)
			return
			
		if not self.transitive:
			return

		for e in grammar.usestates[self.relation]:
			self.visit(e)
			if e in self.result:
				self.result.append(grammar)
				return
		
	def visit_EXPERIMENT(self, grammar):
		if not self.experiment:
			return
			
		if not self.transitive:
			return
			
		if grammar in self.result:
			return

		self.visit(grammar.application)

		if grammar.application in self.result:
			self.result.append(grammar)
