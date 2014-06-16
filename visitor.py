
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

				
##############################################################################


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


##############################################################################


class ScenarioVisitor(Visitor):
	def __init__(self, site = None):
		self.result = []
		self.site = site
		
	def visit_EXPERIMENT(self, grammar):
		if self.site is not None:
			if grammar.site != self.site:
				return

		if not grammar.scenario in self.result:
			self.result.append(grammar.scenario)
		

##############################################################################


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


##############################################################################


class DependencyVisitor(MetaVisitor):
	def __init__(self, relations = ['USES'], se = True, ge = True):
		# self.entities = entities
		self.relations = relations
		self.se = se
		self.ge = ge
		self.nodes = []
		self.edges = []

	def retrieve_edges(self, entity):
		edges = []
		for rel in self.relations:
			edges.extend([(entity, e, rel) for e in entity.usestates[rel]])
		self.edges.extend(edges)
		return [edge[1] for edge in edges]
	
	def visit_SE(self, entity):
		if entity in self.nodes:
			return
		
		if self.se:
			self.nodes.append(entity)
		
		# self.edges.extend(edges)
		# uses_edges = [(entity, e) for e in entity.usestates['USES']]
		# self.edges.extend(uses_edges)
		return self.retrieve_edges(entity)
		
	def visit_APP(self, entity):
		if entity in self.nodes:
			return

		self.nodes.append(entity)
			
		# uses_edges = [(entity, e) for e in entity.usestates['USES']]
		# self.edges.extend(uses_edges)
		# return entity.usestates['USES']
		return self.retrieve_edges(entity)
		
	def visit_GE(self, entity):
		if entity in self.nodes:
			return

		if self.ge:
			self.nodes.append(entity)

		
##############################################################################

import date

class EnablersTestedVisitor(DependencyVisitor):
	def __init__(self, application, se = True, ge = True, ts = None):
		# self.entities = entities
		
		if ts is not None:
			rel = ['WILL USE', 'MAY USE']
			self.ts = date.parse(ts)
		else:
			rel = []
			
		# print('Experiment timestamp: %s  -- %s' % (self.ts, ts))
		
		DependencyVisitor.__init__(self, rel, se, ge)
		
		self.application = application

	def visit(self, meta):
		# print(self.application.identifier)
		# print(self.ts)
		DependencyVisitor.visit(self, self.application)
		self.result = [n for n in self.nodes if n.entity in ['SE', 'GE']]
	
	def retrieve_edges(self, entity):
		# print(entity.identifier)
		if self.ts is None:
			return DependencyVisitor.retrieve_edges(self, entity)
		
		follow = entity.usestates['USES'][:]
		self.edges.extend([(entity, e, 'USES') for e in entity.usestates['USES']])
		
		for rel in self.relations:
			for e in entity.usestates[rel]:
				# print(rel + ' : ' + e.identifier)
				
				if e in entity.timing:
					timeframe = entity.timing[e]
				else:
					continue
				# print(timeframe)
				if timeframe is None:
					continue
					
				if timeframe[1] > self.ts:
					# print("Not yet included")
					continue
				
				self.edges.append((entity, e, rel))
				follow.append(e)
		return follow


##############################################################################

class UsedByVisitor(Visitor):
	def __init__(self, enabler, relations = ['USES'], se = True, app = True, experiment = True, transitive = True):
		self.result = []
		self.enabler = enabler
		self.relations = relations
		self.se = se
		self.app = app
		self.experiment = experiment
		self.transitive = transitive
		
	def visit_Entity(self, grammar):
		if grammar in self.result:
			return

		dep = set()
		for rel in self.relations:
			dep |= set(grammar.usestates[rel])

		if self.enabler in dep:
			self.result.append(grammar)
			return
		
		if not self.transitive:
			return
			
		for e in dep:
			self.visit(e)
		
		if len(set(self.result) & dep) > 0:
			self.result.append(grammar)

	def visit_SE(self, grammar):
		if not self.se:
			return
			
		self.visit_Entity(grammar)

			
			# if self.enabler in grammar.usestates[rel]:
				# self.result.append(grammar)
				# return
			
		# if not len(self.transitive):
			# return
			
		# for transitive in self.transitive:
			# for e in grammar.usestates[transitive]:
				# self.visit(e)
				# if e in self.result:
					# self.result.append(grammar)
					# return
		
		
	def visit_APP(self, grammar):
		if not self.app:
			return
			
		self.visit_Entity(grammar)

		# if grammar in self.result:
			# return

		# if self.enabler in grammar.usestates[self.relation]:
			# self.result.append(grammar)
			# return
			
		# if not len(self.transitive):
			# return

		# for transitive in self.transitive:
			# for e in grammar.usestates[transitive]:
				# self.visit(e)
				# if e in self.result:
					# self.result.append(grammar)
					# return
		
	def visit_EXPERIMENT(self, grammar):
		if not self.experiment:
			return
			
		# if not len(self.transitive):
			# return
		
		if grammar in self.result:
			return

		self.visit(grammar.application)

		if grammar.application in self.result:
			self.result.append(grammar)

			
##############################################################################


class GEVisitor(Visitor):
	def __init__(self):
		self.result = []
		# self.site = site
		# self.scenario = scenario
		
	def visit_GE(self, grammar):
		if grammar in self.result:
			logging.warning("GE %s specified multiple times")
			return
		# if self.site is not None:
			# if grammar.site != self.site:
				# return
		# if self.scenario is not None:
			# if grammar.scenario != self.scenario:
				# return
		self.result.append(grammar)
		

			
##############################################################################


class SEVisitor(Visitor):
	def __init__(self):
		self.result = []
		# self.site = site
		# self.scenario = scenario
		
	def visit_SE(self, grammar):
		if grammar in self.result:
			logging.warning("SE %s specified multiple times")
			return
		# if self.site is not None:
			# if grammar.site != self.site:
				# return
		# if self.scenario is not None:
			# if grammar.scenario != self.scenario:
				# return
		self.result.append(grammar)
		
