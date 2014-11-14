
from . import MetaVisitor
from metastructure import SpecificEnabler, Application, Experiment


class UsedByVisitor(MetaVisitor):
	def __init__(
		self,
		enabler,
		follow_relations = ['USES'],
		collect_entities = [SpecificEnabler, Application, Experiment]
		# transitive = True
	):
		MetaVisitor.__init__(self)
		self.result = []
		self.enabler = enabler
		self.follow_relations = follow_relations
		self.collect_entities = collect_entities
		# self.transitive = transitive
		self.meta = None
	
	def get_result(self):
		return self.result

	def visit_MetaStructure(self, meta):
		# print('visit_MetaStructure')
		self.meta = meta
		follow = [self.enabler]
		# if Experiment in self.collect_entities:
			# follow += self.meta.get_experiments()
		return follow

	# def debug_print_rels(self, rels):
		# for rel in rels:
			# print(rel)

	def get_relations(self, entity):
		rels = self.meta.find_relations(entity)
		# print('rels %d' % len(rels))
		# self.debug_print_rels(rels)

		follow_rel_types = [rel for rel in rels if rel[2] in self.follow_relations]
		# print('follow_rel_types %d' % len(follow_rel_types))
		# self.debug_print_rels(follow_rel_types)

		follow_rels = [dep[0] for dep in follow_rel_types if dep[1] == entity]
		# print('follow_rels %d' % len(follow_rels))
		# self.debug_print_rels(follow_rels)

		return follow_rels
		
	def visit_GenericEnabler(self, entity):
		# print('visit_GenericEnabler %s' % entity)
		return self.get_relations(entity)
	
	def visit_SpecificEnabler(self, entity):
		# print('visit_SpecificEnabler %s' % entity)
		if entity in self.result:
			return
		if SpecificEnabler in self.collect_entities:
			self.result.append(entity)
		return self.get_relations(entity)
	
	def visit_Application(self, entity):
		# print('visit_Application %s' % entity)
		if entity in self.result:
			return
		if Application in self.collect_entities:
			self.result.append(entity)
		return None # [exp for exp in self.meta.get_experiments() if exp.get_application() == entity]

	# def visit_Experiment(self, entity):
		# print('visit_Experiment %s' % entity)
		# if Experiment not in self.collect_entities:
			# return
		# if entity in self.result:
			# return
		# if entity.get_application() in self.result:
			# self.result.append(entity)


