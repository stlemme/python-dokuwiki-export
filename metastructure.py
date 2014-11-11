
import wikiutils
import logging
from metaprocessor import MetaData, MetaProcessor
from metagrammar import *
from specificenabler import SpecificEnabler

class Entity(object):
	pass

class NamedEntity(Entity):
	def __init__(self, name):
		self.name = name
		
	def get_name(self):
		return self.name
	
	
class GenericEnabler(NamedEntity):
	pass

class Location(NamedEntity):
	pass

class Scenario(NamedEntity):
	pass
	


# class Application(NamedEntity):
	# def __init__(self, name, provider):
		# Entity.__init__(self, name)
		# self.provider = provider
	
	
# class Scenario(NamedEntity):
	# def __init__(self, name):
		# Entity.__init__(self, name)



class MetaStructure(object):
	def __init__(self):
		self.ast = None
		self.data = None
		
		self.ges = []
		self.ses = []
		self.apps = []

		self.locations = []
		self.scenarios = []

		self.edges = []
		
	# def add_generic_enabler(self, ge):
		# self.ges.append(ge)

	# def add_specific_enabler(self, se):
		# self.ses.append(se)
		
	# def add_location(self, loc):
		# self.locations.append(loc)

	# def add_scenario(self, scenario):
		# self.scenarios.append(scenario)

	def get_ast(self):
		return self.ast

	def get_data(self):
		return self.data
		
	def set_ast(self, ast, data):
		self.ast = ast
		self.data = data
	
	def extract_basic_entities(self):
		self.extract_named_entities(GenericEnabler, GenericEnablerStmt, self.ges)
		self.extract_named_entities(Location, LocationStmt, self.locations)
		self.extract_named_entities(Scenario, ScenarioStmt, self.scenarios)
		
	def extract_ses(self, dw, partners, licenses, pub):
		stmts = self.ast.find_all(SpecificEnablerStmt)
		for sestmt in stmts:
			id = sestmt.get_identifier()
			logging.info('Processing %s %s' % (sestmt.get_keyword(), id))
			
			se_meta_page = sestmt.get_meta_page()
			print(se_meta_page)
			if se_meta_page is None:
				logging.warning('Missing reference to meta page of SE. Skip!')
				continue
			
			se = SpecificEnabler.load(dw, se_meta_page, licenses, partners, pub)
			container.append(entity)
			self.data.map(stmt, entity)

	def extract_apps(self, partners, licenses, pub):
		pass
		
	def extract_experiments(self, partners, licenses, pub):
		pass
		
	def extract_named_entities(self, EntityClass, StmtClass, container):
		stmts = self.ast.find_all(StmtClass)
		for stmt in stmts:
			id = stmt.get_identifier()
			logging.info('Processing %s %s' % (stmt.get_keyword(), id))
			entity = EntityClass(id)
			container.append(entity)
			self.data.map(stmt, entity)


	@staticmethod
	def load(dw, meta_page, partners, licenses, pub):
		ms = MetaStructure()
		
		logging.info("Loading page of meta structure %s ..." % meta_page)
		page = dw.getpage(meta_page)
		if page is None:
			return None
		doc = wikiutils.strip_code_sections(page)
		metadoc = '\n'.join(doc)

		meta_data = MetaData(partners, logging.warning, logging.error)
		
		mp = MetaProcessor(meta_data)
		
		logging.info("Processing meta structure ...")
		meta_ast = mp.process(metadoc)
		if meta_ast is None:
			return ms
		
		ms.set_ast(meta_ast, meta_data)

		ms.extract_basic_entities()
		ms.extract_ses(dw, partners, licenses, pub)
		ms.extract_apps(partners, licenses, pub)
		ms.extract_experiments(partners, licenses, pub)
		
		return ms
	