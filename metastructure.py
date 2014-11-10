
import wikiutils
import logging
from metaprocessor import MetaData, MetaProcessor
from metagrammar import GenericEnablerStmt


class Entity(object):
	pass

class NamedEntity(Entity):
	def __init__(self, name):
		self.name = name
		
	def get_name(self):
		return self.name
	
	
class GenericEnabler(NamedEntity):
	def __init__(self, name):
		NamedEntity.__init__(self, name)
	
	
# class Application(NamedEntity):
	# def __init__(self, name, provider):
		# Entity.__init__(self, name)
		# self.provider = provider
	
	
# class Scenario(NamedEntity):
	# def __init__(self, name):
		# Entity.__init__(self, name)



class MetaStructure(object):
	def __init__(self):
		# self.meta_ast = None
		# self.meta_data = None
		self.ges = []
		self.ses = []
		self.apps = []

		self.locations = []
		self.scenarios = []

		self.edges = []
		
	def add_generic_enabler(self, ge):
		self.ges.append(ge)

	def add_specific_enabler(self, se):
		self.ses.append(se)
		
	def add_location(self, loc):
		self.locations.append(loc)

	def add_scenario(self, scenario):
		self.scenarios.append(scenario)


	@staticmethod
	def load(dw, meta_page, partners):
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
		
		gestmts = mp.get_stmts(meta_ast, GenericEnablerStmt)
		for gestmt in gestmts:
			ge = GenericEnabler(gestmt.get_identifier())
			ms.add_generic_enabler(ge)
			meta_data.map(gestmt, ge)
		
		# ms.set_structure(meta_ast)
		# ms.set_data(meta_data)
		
		return ms
	