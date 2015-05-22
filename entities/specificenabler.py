
from . import NamedEntity
import logging
import wikiutils
import json
from catalogauto import *
from jsonschema.jsonschema import validate, ValidationError, SchemaError


class SpecificEnabler(NamedEntity):

	def __init__(self, metapage):
		NamedEntity.__init__(self, 'SE at %s' % metapage)
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
		
	def get_name(self):
		return self.get_naming_conventions().fullname()

	def get_metapage(self):
		return self.metapage
		
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
		examples = self.get('/spec/examples/additional')
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
		if meta is None:
			return se
		
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

		
	@staticmethod
	def perform_sanity_checks(se):
		r = True
		
		# ID
		#  -> normalized name
		# Name (M)
		r &= val_value(se, '/spec/name', val_length, (1, 50))
		# Short-description (M)
		r &= val_value(se, '/spec/documentation/tag-line', val_length, (0, 150))
		# Categories (M)
		#  -> platforms
		# Tags (M)
		
		# Additional-tags (O)
		
		# Supplier (M)
		#  -> nice owners
		# Thumbnail (M)
		r &= val_value(se, '/auto/media/thumbnail', val_exists)
		
		# What-it-does (M)
		r &= val_value(se, '/spec/documentation/what-it-does', val_length, (200, 600))
		# How-it-works (M)
		r &= val_value(se, '/spec/documentation/how-it-works', val_length, (200, 800))
		# Why-you-need-it (M)
		r &= val_value(se, '/spec/documentation/why-you-need-it', val_length, (150, 600))
		
		# Terms-and-conditions within FI-PPP (M)
		r &= val_value(se, '/spec/license/summary', val_length, (50, 600))
		r &= val_value(se, '/spec/license/copyright', val_length, (0, 300))
		# Terms-and-conditions beyond FI-PPP (M)

		# Delivery-mode (M)
		r &= val_value(se, '/auto/delivery/model', val_inlist, ['Source', 'Binary', 'SaaS'])
		model = se.get('/auto/delivery/model')
		# Delivery-artifact (M)
		r &= val_value(se, '/spec/delivery/description', val_length, (50, 300))
		
		# Docker-Image (M for Source and Binary)
		# SaaS-production-instance (M for SaaS)
		if model == 'SaaS':
			r &= val_value(se, '/spec/delivery/instances/public/endpoint', val_url)
		# Github repository (M for Source)
		if model == 'Source':
			r &= val_value(se, '/spec/delivery/repository/github', val_url)
		# ? Binaries?
		# Downloadable-source-code (M for Source)
		if model == 'Source':
			r &= val_value(se, '/spec/delivery/sources', val_url)
		# SE specification
		r &= val_value(se, '/auto/documentation/wiki-url', val_url)
		# Programming-Guide (M)
		r &= val_value(se, '/auto/documentation/devguide-url', val_url)
		# Installation-guide (M)
		r &= val_value(se, '/auto/documentation/installguide-url', val_url)
		# API (M)
		r &= val_value(se, '/auto/documentation/api-url', val_url)
		# Online-demo (M)
		r &= val_value(se, '/auto/usage/online-demo/link', val_url)
		# ? Example-scripts (M)
		# Tutorial (O)
		if val_value(se, '/auto/usage/tutorials', val_url, warning=False):
			logging.info("Tutorials recognized.")
		# Video-Teaser (O) - should be mandatory
		# Video-Tutorial (O)
		# Playground-Image (O)
		if val_value(se, '/auto/usage/playground/link', val_url, warning=False):
			logging.info("Playground examples recognized.")
			r &= val_value(se, '/auto/usage/playground/link', val_pattern, "^https://github.com/(.+)/(.+)")
		# FAQ (O)
		if val_value(se, '/auto/support/faq-url', val_url, warning=False):
			logging.info("FAQ recognized.")
		# Contact (M)
		#  -> contact persons from partners page
		# Bug-report (M)
		r &= val_value(se, '/auto/support/bugtracker', val_url)
		# ? Support-request (M)
		
		return r

def val_value(se, path, val, args = None, warning=True):
	s = se.get(path)
	issue = val(s, args)
	if issue is None:
		return True
	if warning:
		logging.warning(issue.format(var=path))
	return False

def val_exists(s, args):
	return "{var} is not specified" if s is None else None


def val_length(s, args):
	issue = val_exists(s, None)
	if issue is not None:
		return issue
	l = len(s)
	if l < args[0]:
		return "{{var}} is too short (min {d} chars)".format(d=args[0])
	if l > args[1]:
		return "{{var}} is too long (max {d} chars)".format(d=args[1])
	return None

def val_url(s, args):
	issue = val_exists(s, None)
	if issue is not None:
		return issue

	# TODO: check url response code regarding valid resource for deep sanity checks
	
	return None
	
def val_inlist(s, args):
	issue = val_exists(s, None)
	if issue is not None:
		return issue
	if s in args:
		return None
		
	return "{{var}} is none out of [{val}]".format(val=', '.join(args))

def val_pattern(s, args):
	issue = val_exists(s, None)
	if issue is not None:
		return issue

	if re.match(args, s) is None:
		return "{{var}} does not match pattern {val}".format(val=args)
	
	return None
