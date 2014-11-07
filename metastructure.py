
import wikiutils
import logging
from metaprocessor import MetaData, MetaProcessor


class MetaStructure(object):
	def __init__(self):
		self.meta_ast = None
		self.meta_data = None
		self.edges = []
	
	def set_structure(self, meta_ast):
		self.meta_ast = meta_ast
		
	def get_structure(self):
		return self.meta_ast

	def set_data(self, meta_data):
		self.meta_data = meta_data
		
	def get_data(self):
		return self.meta_data
		
	
	@staticmethod
	def load(dw, meta_page, partners):
		ms = MetaStructure()
		
		# logging.info("Loading page of meta structure %s ..." % meta_page)
		page = dw.getpage(meta_page)
		if page is None:
			return None
		doc = wikiutils.strip_code_sections(page)
		metadoc = '\n'.join(doc)

		meta_data = MetaData(partners, logging.warning, logging.error)
		
		mp = MetaProcessor(meta_data)
		
		# logging.info("Processing meta structure ...")
		meta_ast = mp.process(metadoc)
		
		ms.set_structure(meta_ast)
		ms.set_data(meta_data)
		
		return ms
	