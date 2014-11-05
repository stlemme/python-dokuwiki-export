
import wikiutils
from metaprocessor import MetaProcessor


class MetaStructure(object):
	def __init__(self):
		self.meta_structure = None
	
	def set_structure(self, meta_structure):
		self.meta_structure = meta_structure
		
	def get_structure(self):
		return self.meta_structure
		
	
	@staticmethod
	def load(dw, meta_page, meta_data, partners):
		ms = MetaStructure()
		
		# logging.info("Loading page of meta structure %s ..." % meta_page)
		page = dw.getpage(meta_page)
		if page is None:
			return None
		doc = wikiutils.strip_code_sections(page)
		metadoc = '\n'.join(doc)
		
		# data = MetaData(logging.warning, logging.error)
		
		mp = MetaProcessor(meta_data)
		
		# logging.info("Processing meta structure ...")
		meta = mp.process(metadoc)
		
		ms.set_structure(meta)
		return ms
	