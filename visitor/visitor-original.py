
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


##############################################################################


class ExperimentsVisitor(Visitor):
	def __init__(self, site = None, scenario = None):
		self.result = []
		self.site = site
		self.scenario = scenario
		
	def visit_Experiment(self, exp):
		if self.site is not None:
			if exp.get_site() != self.site:
				return

		if self.scenario is not None:
			if exp.get_scenario() != self.scenario:
				return
		
		self.result.append(exp)

	def get_result(self):
		return self.result

##############################################################################


class TestedScenarioVisitor(Visitor):
	def __init__(self, site = None):
		self.result = []
		self.site = site
		
	def visit_Experiment(self, exp):
		if self.site is not None:
			if exp.get_site() != self.site:
				return
				
		scenario = exp.get_scenario()
		if scenario in self.result:
			return
			
		self.result.append(scenario)
		
	def get_result(self):
		return self.result
		

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


class UsedByVisitor(MetaVisitor):
	def __init__(
		self,
		enabler,
		follow_relations = ['USES'],
		collect_entities = [SpecificEnabler, Application, Experiment],
		transitive = True
	):
		self.result = []
		self.enabler = enabler
		self.follow_relations = follow_relations
		self.collect_entities = collect_entities
		self.transitive = transitive
		self.meta = None
	
	def visit_MetaStructure(self, meta):
		self.meta = meta
		return [self.enabler]

	def visit_Entity(self, entity):
		if entity in self.result:
			return

		dep = set()
		for rel in self.relations:
			dep |= set(entity.usestates[rel])

		if self.enabler in dep:
			self.result.append(entity)
			return
		
		if not self.transitive:
			return
			
		for e in dep:
			self.visit(e)
		
		if len(set(self.result) & dep) > 0:
			self.result.append(grammar)

	
	def visit_SpecificEnabler(self, entity):
		if SpecificEnabler not in self.collect_entities:
			return
		self.visit_Entity(entity)

	
	def visit_Application(self, entity):
		if Application not in self.collect_entities:
			return
		self.visit_Entity(entity)

	def visit_Experiment(self, entity):
		if Experiment not in self.collect_entities:
			return
		
		# if not len(self.transitive):
			# return
		
		if entity in self.result:
			return

		self.visit(grammar.application)

		if grammar.application in self.result:
			self.result.append(grammar)

			
##############################################################################


# class GEVisitor(Visitor):
	# def __init__(self):
		# self.result = []
		# self.site = site
		# self.scenario = scenario
		
	# def visit_GE(self, grammar):
		# if grammar in self.result:
			# logging.warning("GE %s specified multiple times")
			# return
		# if self.site is not None:
			# if grammar.site != self.site:
				# return
		# if self.scenario is not None:
			# if grammar.scenario != self.scenario:
				# return
		# self.result.append(grammar)
		

			
##############################################################################


# class SEVisitor(Visitor):
	# def __init__(self):
		# self.result = []
		# self.site = site
		# self.scenario = scenario
		
	# def visit_SE(self, grammar):
		# if grammar in self.result:
			# logging.warning("SE %s specified multiple times")
			# return
		# if self.site is not None:
			# if grammar.site != self.site:
				# return
		# if self.scenario is not None:
			# if grammar.scenario != self.scenario:
				# return
		# self.result.append(grammar)
		
