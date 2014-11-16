
import wikiutils
import logging
from metaprocessor import MetaAdapter, MetaProcessor
from metagrammar import *
from entities import *



class MetaStructure(Entity):
	def __init__(self):
		self.ast = None
		self.adapter = None
		
		self.ges = []
		self.ses = []
		self.apps = []

		self.locations = []
		self.scenarios = []
		
		self.experiments = []

		self.invalid = []

		self.edges = []
	
	
	def get_ast(self):
		return self.ast

	def get_adapter(self):
		return self.adapter

	def get_descendants(self):
		return self.ges + self.ses + self.apps + self.locations + self.scenarios + self.experiments + self.invalid

	
	
	def find_dependencies(self, entity):
		return [dep[1:3] for dep in self.edges if dep[0] == entity]
	
	def find_edges(self, entity1, entity2):
		return [dep for dep in self.edges if dep[0] == entity1 and dep[1] == entity2]

	def find_relations(self, entity):
		return [dep for dep in self.edges if dep[0] == entity or dep[1] == entity]

	
	def find_enabler(self, id):
		enabler = self.adapter.find(id)
		if enabler in self.ges:
			return enabler
		if enabler in self.ses:
			return enabler
		if isinstance(enabler, InvalidEntity) and enabler.get_keyword() in ['GE', 'SE']:
			return enabler
		return None

	def find_application(self, id):
		app = self.adapter.find(id)
		if app in self.apps:
			return app
		return None
	
	def find_location(self, id):
		loc = self.adapter.find(id)
		if loc in self.locations:
			return loc
		return None

	def find_scenario(self, id):
		scenario = self.adapter.find(id)
		if scenario in self.scenarios:
			return scenario
		return None
	
	def get_experiments(self, site = None):
		if site is None:
			return self.experiments
		return [exp for exp in self.experiments if exp.get_site() == site]

	def get_generic_enablers(self):
		return self.ges

	def get_specific_enablers(self):
		return self.ses

		
	def set_ast(self, ast, adapter):
		self.ast = ast
		self.adapter = adapter
		
	def declare_invalid_stmt(self, stmt):
		invalid = InvalidEntity(stmt.get_keyword(), stmt.get_identifier())
		self.adapter.map(stmt, invalid)
		self.invalid.append(invalid)
	
	
	def extract_basic_entities(self):
		logging.info("Extract Generic Enablers")
		self.extract_named_entities(GenericEnabler, GenericEnablerStmt, self.ges)
		logging.info("Extract deployment locations")
		self.extract_named_entities(Location, LocationStmt, self.locations)
		logging.info("Extract scenarios")
		self.extract_named_entities(Scenario, ScenarioStmt, self.scenarios)
	
	def extract_ses(self, dw, partners, licenses, pub):
		stmts = self.ast.find_all(SpecificEnablerStmt)
		for sestmt in stmts:
			id = sestmt.get_identifier()
			logging.debug('Processing %s %s' % (sestmt.get_keyword(), id))
			
			se_meta_page = sestmt.get_meta_page()

			if se_meta_page is None:
				logging.warning('SE %s lacks of a reference to its meta page. Skip!' % id)
				self.declare_invalid_stmt(sestmt)
				continue
			
			se = SpecificEnabler.load(dw, se_meta_page, licenses, partners, pub)

			if not se.is_valid():
				logging.warning('SE %s has no valid information at its meta page at %s. Skip!' % (id, se_meta_page))
				self.declare_invalid_stmt(sestmt)
				continue

			self.ses.append(se)
			self.adapter.map(sestmt, se)
			
			self.add_dependencies(se, sestmt.get_dependencies())

	def extract_apps(self, partners):
		stmts = self.ast.find_all(ApplicationStmt)
		for appstmt in stmts:
			id = appstmt.get_identifier()
			logging.debug('Processing %s %s' % (appstmt.get_keyword(), id))
			
			developer = partners.get_person(appstmt.get_originator())
			if developer is None:
				logging.warning('Developer of application "%s" is unknown.' % id)

			app = Application(id, developer)

			self.apps.append(app)
			self.adapter.map(appstmt, app)
			
			self.add_dependencies(app, appstmt.get_dependencies())
	
	
	def add_dependencies(self, entity, dependencies):
		for state, depid, timing in dependencies:
			depentity = self.find_enabler(depid)
			# print(depentity, state, timing)
			if depentity is None:
				logging.warning('%s refers to unknown dependency "%s" - it is ignored!' % (entity, depid))
				continue
				
			if isinstance(depentity, InvalidEntity):
				logging.warning('%s refers to dependency "%s" (%s), which contain invalid/insufficient information - it is ignored!' % (entity, depid, depentity))
				continue
			
			# TODO: validate timing
			self.edges.append((entity, depentity, state, timing))
		
	
	def extract_experiments(self, partners):
		stmts = self.ast.find_all(ExperimentStmt)
		for expstmt in stmts:
			site = expstmt.get_site()
			date = expstmt.get_date()
			logging.debug('Processing experiment of site %s at %s' % (site, date))
			
			conductor = partners.get_person(expstmt.get_originator())
			if conductor is None:
				logging.warning('Conductor of experiment at site "%s" is unknown - Skip!' % site)
				continue
			
			place = expstmt.get_place()

			exp = Experiment(site, date, conductor, place)

			scenarioid = expstmt.get_scenario()
			scenario = self.find_scenario(scenarioid)
			if scenario is None:
				logging.warning('%s refers to unknown scenario "%s" - Skip!' % (exp, scenarioid))
				continue
			
			appid = expstmt.get_application()
			app = self.find_application(appid)
			if app is None:
				logging.warning('%s refers to unknown application "%s" - Skip!' % (exp, appid))
				continue
			
			exp.set_scenario(scenario, app)
			
			deployments = expstmt.get_deployments()
			
			for enablerid, locationid in deployments.items():
				enabler = self.find_enabler(enablerid)
				if enabler is None:
					logging.warning('%s refers to unknown enabler "%s" - it is ignored!' % (exp, enablerid))
					continue
					
				if isinstance(enabler, InvalidEntity):
					logging.warning('%s refers to enabler "%s" (%s), which contain invalid/insufficient information - it is ignored!' % (exp, enablerid, enabler))
					continue

				location = self.find_location(locationid)
				if location is None:
					logging.warning('%s refers to unknown deployment location "%s" - it is ignored!' % (exp, locationid))
					continue
					
				exp.set_enabler_location(enabler, location)

			self.experiments.append(exp)
			

			
	def extract_named_entities(self, EntityClass, StmtClass, container):
		stmts = self.ast.find_all(StmtClass)
		for stmt in stmts:
			id = stmt.get_identifier()
			logging.debug('Processing %s %s' % (stmt.get_keyword(), id))
			entity = EntityClass(id)
			container.append(entity)
			self.adapter.map(stmt, entity)

	
	
	@staticmethod
	def load(dw, meta_page, partners, licenses, pub):
		ms = MetaStructure()
		
		logging.info("Loading page of meta structure %s ..." % meta_page)
		page = dw.getpage(meta_page)
		if page is None:
			return None
		doc = wikiutils.strip_code_sections(page)
		metadoc = '\n'.join(doc)

		meta_adapter = MetaAdapter(partners)
		
		mp = MetaProcessor(meta_adapter)
		
		logging.info("Parsing meta structure ...")
		meta_ast = mp.process(metadoc)
		if meta_ast is None:
			return None
		logging.info("Finished parsing.")
		
		ms.set_ast(meta_ast, meta_adapter)

		logging.info("Processing meta structure ...")

		ms.extract_basic_entities()
		
		logging.info("Extract Specific Enablers")
		ms.extract_ses(dw, partners, licenses, pub)
		
		logging.info("Extract applications")
		ms.extract_apps(partners)
		
		logging.info("Extract experiments")
		ms.extract_experiments(partners)

		logging.info("Meta structure successfully loaded.")
		
		return ms
	