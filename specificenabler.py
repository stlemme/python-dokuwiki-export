
from jsonutils import Values
import logging
import wikiutils
import json
from catalogauto import *
from jsonschema.jsonschema import validate, ValidationError, SchemaError


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
	
	def resolve(self, ref, dw, pub):
		if ref.startswith('http'):
			return ref
			
		info = dw.pageinfo(ref)
		if info is not None:
			pub_page = pub.public_page(ref)
			if pub_page is None:
				logging.warning("Referencing to private page %s" % ref)
				return "[private] " + ref
				
			puburl = dw.pageurl(pub_page)
			return puburl
			
		info = dw.fileinfo(ref)
		if info is not None:
			pub_file = pub.public_file(ref)
			if pub_file is None:
				logging.warning("Referencing to private file %s" % ref)
				return "[private] " + ref
				
			puburl = dw.fileurl(pub_file)
			return puburl
		
		return "[unresolved] " + ref

	
	def resolve_wiki_references(self, dw, pub):
		examples = self.get('/spec/examples')
		if examples is not None:
			for k in examples:
				examples[k]['link'] = self.resolve(examples[k]['link'], dw, pub)
		
		images = self.get('/spec/media/images')
		if images is not None:
			for k in images:
				images[k] = self.resolve(images[k], dw, pub)

				
	@staticmethod
	def load(dw, se_meta_page, licenses, partners, pub):
		se = SpecificEnabler(se_meta_page)

		meta = dw.getpage(se_meta_page)
		metadata = wikiutils.strip_code_sections(meta)
		metajson = '\n'.join(metadata)
		
		se.set_metajson(metajson)

		try:
			se_spec = json.loads(metajson)
		except ValueError as e:
			logging.warning("Unable to read meta data from page %s. No valid JSON!\n%s" % (se_meta_page, e))
			return se

		schema = None
		with open('se-meta-schema.json', 'r') as schema_file:
			schema = json.load(schema_file)
		
		if schema is None:
			logging.warning("Could not validate json schema due to missing schema file")
			return se
		
		try:
			validate(se_spec, schema)
		except ValidationError as e:
			logging.warning("Invalid meta data for SE at %s.\n%s" % (se_meta_page, e))
			return se
		except SchemaError as e:
			logging.warning("Could not validate json schema due to an invalid json schema.\n%s" % e)
			return se
				
		se.set_metaspec(se_spec)
		
		se.setup_naming_conventions(dw)

		se.fill_license(licenses)
		se.fill_contacts(partners)
		se.fill_auto_values(dw, pub)
		se.fill_nice_owners(partners)
		se.resolve_wiki_references(dw, pub)
		
		se.set_valid()
		
		return se
