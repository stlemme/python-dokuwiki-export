
from jsonutils import Values
import logging
import preprocess
import json
from catalogauto import *



class SpecificEnabler(Values):

	def __init__(self, metapage):
		Values.__init__(self)
		self.valid = False
		self.metapage = metapage

	def set_metajson(self, metajson):
		self.set('/metajson', metajson)
	
	def set_metaspec(self, spec):
		self.set('/spec', spec)
		
	def set_valid(self, valid = True):
		self.valid = valid
	
	def setup_naming_conventions(self, dw):
		self.nc = NamingConventions(dw, self.get('/spec'))
		
	def is_valid(self):
		return self.valid
	
	def get_naming_conventions(self):
		return self.nc
		
	def fill_license(self, licenses):
		lic = self.get('/spec/license')
		lic = licenses.process(lic)
		self.set('/spec/license', lic)

	def fill_nice_owners(self, partners):
		self.set('/auto/nice-owners', self.nice_owners(partners))
		
	def nice_owners(self, partners):
		owners = self.get('/spec/owners')
		if owners is None:
			logging.warning("No owner defined!")
			return '[[NO-OWNER-DEFINED]]'
		
		niceowners = []
		for o in owners:
			shortname = partners.get('/' + o + '/company/shortname')
			if shortname is None:
				shortname = o
			niceowners.append(shortname)
		
		if len(niceowners) == 1:
			return niceowners[0]
		
		# print(niceowners)
		
		nice = ', '.join(niceowners[:-1])
		nice += ' and ' + niceowners[-1]
		return nice

	def fill_contacts(self, partners):
		r = {}
		primary = self.handle_primary_contact(partners)
		if primary is None:
			r['technical'] = self.handle_contacts('technical', partners)
			r['legal'] = self.handle_contacts('legal', partners)
			contacts = self.get('/spec/contacts');
			for name in contacts:
				r[name] = partners.get_person(name)
		else:
			r['primary'] = primary
			
		
		self.set('/auto/contacts', r)
	
	def handle_contacts(self, type, partners):
		contacts = self.get('/spec/contacts');
		r = {}
		for k, v in contacts.items():
			if v != type:
				continue
				
			person = partners.get_person(k)
			if person is None:
				continue

			r[k] = person
		# print(r)
		return r if len(r) > 0 else None
		
	def handle_primary_contact(self, partners):
		primary = self.get('/spec/contacts/primary');
		if primary is None:
			return None
		return partners.get_person(primary)

	def fill_auto_values(self, dw, pub):
		auto = AutoValues(dw, pub, self)
		for k, v in auto.items():
			# print(k, v)
			self.set(k, v)
	
	
	@staticmethod
	def load(dw, se_meta_page, licenses, partners, pub):
		se = SpecificEnabler(se_meta_page)

		meta = dw.getpage(se_meta_page)
		metadata = preprocess.preprocess(meta)
		metajson = '\n'.join(metadata)
		
		se.set_metajson(metajson)

		try:
			se_spec = json.loads(metajson)
		except ValueError as e:
			logging.warning("Unable to read meta data from page %s. No valid JSON!\n%s" % (se_meta_page, e))
			return se

		# TODO: json schema validation
		
		se.set_metaspec(se_spec)
		
		se.setup_naming_conventions(dw)

		se.fill_license(licenses)
		se.fill_contacts(partners)
		se.fill_auto_values(dw, pub)
		se.fill_nice_owners(partners)
		
		se.set_valid()
		
		return se
