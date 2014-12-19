

import json
import wikiutils
import logging
import mirror
# import releases
import date
from publisher import *
from licenses import Licenses
from partners import Partners
from entities import SpecificEnabler
from metastructure import MetaStructure


meta_page = {
	'partners': ':ficontent:private:meta:partner',
	'licenses': ':ficontent:private:meta:license',
	'structure': ':ficontent:private:meta:start'
}


class FIdoc(object):
	def __init__(self, dw):
		self.dw = dw
		self.partners = Partners(self.load_json_from_wiki(self.get_meta_page('partners')))
		self.licenses = Licenses(self.load_json_from_wiki(self.get_meta_page('licenses')))

		pub_pages = mirror.public_pages(self.dw)

		self.pub = wikipublisher(self.dw, pub_pages, mirror.rx_exceptions, mirror.export_ns)
		self.meta = MetaStructure.load(
			self.dw,
			self.get_meta_page('structure'),
			self.partners,
			self.licenses,
			self.pub
		)
		self.ses = {}
	
	def get_wiki(self):
		return self.dw
	
	def get_partners(self):
		return self.partners

	def get_licenses(self):
		return self.licenses
	
	
	def get_publisher(self):
		return self.pub
		
	def get_specific_enabler(self, metapage):
		if metapage not in self.ses:
			self.ses[metapage] = SpecificEnabler.load(self.dw, metapage, self.licenses, self.partners, self.pub)
		return self.ses[metapage]

	def get_meta_structure(self):
		return self.meta
		
	def list_all_se_meta_pages(self):
		all_pages_info = self.dw.allpages()
		meta_pages = []
		
		for info in all_pages_info:
			fullname = self.dw.resolve(info['id'])
			if fullname is None:
				continue

			if mirror.rx_meta_pages.match(fullname) is None:
				continue
			
			meta_pages.append(fullname)
			
		return meta_pages
		

		
	def load_json_from_file(self, filename, default = {}):
		with open(filename) as json_file:
			return json.load(json_file)
		return default

	def load_json_from_wiki(self, wikipage, default = {}):
		page = self.dw.getpage(wikipage)
		doc = wikiutils.strip_code_sections(page)
		data = '\n'.join(doc)
		try:
			return json.loads(data)
		except ValueError as e:
			logging.warning("Unable to read json data from page %s. No valid JSON!" % wikipage)
		return default

	def load_code_from_wiki(self, wikipage):
		page = self.dw.getpage(wikipage)
		if page is None:
			return None
		doc = wikiutils.strip_code_sections(page)
		return '\n'.join(doc)

	def get_meta_page(self, page_name):
		if page_name not in meta_page:
			return None
		return meta_page[page_name]
		
		
	