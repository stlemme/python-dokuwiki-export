

import logging
from wiki import *
from namingconventions import *
from publisher import *


class AutoValues(object):
	def __init__(self, dw, pub, values):
		self.dw = dw
		self.pub = pub
		self.values = values
		self.nc = NamingConventions(self.dw, self.values.get('/spec'))
	
	def items(self):
		auto_values = {
			'nice-owners': self.nice_owners,
			'documentation': {
				'wiki-url': self.pub_se_wiki_url,
				'devguide-url': self.pub_se_devguide_url
			},
			'delivery': {
				'hosted-service': self.delivers_hosted_service,
				'source-code': self.delivers_source_code,
				'package': self.delivers_package
			},
			'license': {
				'is-open-source': self.is_open_source,
				'is-proprietary': self.is_proprietary,
				'has-evaluation': self.has_evaluation
			}
		}
		
		items = {}
		self.process_auto_values(auto_values, '/auto', items)
		return items.items()

	def process_auto_values(self, obj, path, items):
		for k, v in obj.items():
			p = path + '/' + k
			if type(v) is dict:
				self.process_auto_values(v, p, items)
			else:
				# print(v)
				items[p] = v()
		
	def nice_owners(self):
		owners = self.values.get('/spec/owners')
		if owners is None:
			logging.warning("No owner defined!")
			return '[[NO-OWNER-DEFINED]]'
		
		if len(owners) == 1:
			return owners[0]
		
		nice = ', '.join(owners[:-1])
		nice += ' and ' + owners[-1]
		return nice

	def pub_se_wiki_url(self):
		page = self.nc.wikipage()
		pub_page = self.pub.public_page(page)
		return self.dw.pageurl(pub_page)

	def pub_se_devguide_url(self):
		page = self.nc.devguide()
		pub_page = self.pub.public_page(page)
		return self.dw.pageurl(pub_page)

	def is_open_source(self):
		return self.YesNo(self.values.get('/spec/license/type') == 'open')
		
	def is_proprietary(self):
		return self.YesNo(self.values.get('/spec/license/type') == 'prop')

	def has_evaluation(self):
		return self.YesNo(self.values.get('/spec/license/type') == 'eval')

	def delivers_hosted_service(self):
		return self.YesNo(self.values.get('/spec/delivery/instance') is not None)
		
	def delivers_source_code(self):
		sources = self.values.get('/spec/delivery/source-code') is not None
		repo = self.values.get('/spec/delivery/repository') is not None
		return self.YesNo(sources or repo)
	
	def delivers_package(self):
		sources = self.values.get('/spec/delivery/source-code') is not None
		binary = self.values.get('/spec/delivery/binary') is not None
		return self.YesNo(sources or binary)
	
	def YesNo(self, cond):
		return 'Yes' if cond else 'No'
