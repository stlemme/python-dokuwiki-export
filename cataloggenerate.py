#!/usr/bin/env python


import logging
from wiki import *
import re
import json
from collections import deque
from publisher import *
import mirror
from catalogauto import *
import preprocess
import releases


def json_get(json_data, path):
	parts = deque(path[1:].split('/'))
	obj = json_data
	while len(parts) > 0:
		if obj is None:
			return None
		prop = parts.popleft()
		if prop not in obj:
			return None
		obj = obj[prop]
	return obj

def json_set(json_data, path, data):
	parts = deque(path[1:].split('/'))
	obj = json_data
	while len(parts) > 1:
		prop = parts.popleft()
		if prop not in obj:
			obj[prop] = {}
		obj = obj[prop]
	obj[parts[-1]] = data


class Values(object):
	def __init__(self, values = None):
		self.values = {} if values is None else values

	def get(self, path):
		return json_get(self.values, path)

	def set(self, path, data):
		json_set(self.values, path, data)
	

class CatalogGenerator(object):

	def __init__(self, dw, pub, template):
		self.dw = dw
		self.pub = pub
		self.template = template
		self.values = None
		self.license_templates = self.load_json_from_wiki(':ficontent:private:meta:license')
		self.partner_contacts = self.load_json_from_wiki(':ficontent:private:meta:partner')
	
	def load_json_from_file(self, filename, default = {}):
		with open(filename) as json_file:
			return json.load(json_file)
		return default

	def load_json_from_wiki(self, wikipage, default = {}):
		page = dw.getpage(wikipage)
		doc = preprocess.preprocess(page)
		data = '\n'.join(doc)
		try:
			return json.loads(data)
		except ValueError as e:
			logging.warning("Unable to read json data from page %s. No valid JSON!" % wikipage)
		return default
		
	def generate_entry(self, spec):
		self.values = Values({
			"spec": spec
		})
		self.fill_license()
		self.fill_contacts()
		self.fill_auto_values()
		self.fill_nice_owners()
		
		entry = self.template
		
		entry = self.process_text_snippet(entry)
		self.values = None
		
		return entry
		
	def fill_license(self):
		lic = self.values.get('/spec/license')
		if lic is None:
			logging.warning("No license information available!")
			return
		if 'template' not in lic:
			return
		template = lic['template']
		if template not in self.license_templates:
			logging.warning("Invalid license template %s" % template)
			return
		ovrlic = lic
		lic = self.license_templates[template]
		for k, v in ovrlic.items():
			lic[k] = v
		self.values.set('/spec/license', lic)

	def fill_nice_owners(self):
		self.values.set('/auto/nice-owners', self.nice_owners())
		
	def nice_owners(self):
		owners = self.values.get('/spec/owners')
		if owners is None:
			logging.warning("No owner defined!")
			return '[[NO-OWNER-DEFINED]]'
		
		niceowners = []
		for o in owners:
			p = self.get_partner(o)
			if p is None:
				continue
			c = p['company']
			if 'shortname' not in c:
				continue
			niceowners.append(c['shortname'])
		
		if len(niceowners) == 1:
			return niceowners[0]
		
		# print(niceowners)
		
		nice = ', '.join(niceowners[:-1])
		nice += ' and ' + niceowners[-1]
		return nice

	def fill_contacts(self):
		r = {}
		primary = self.handle_primary_contact()
		if primary is None:
			r['technical'] = self.handle_contacts('technical')
			r['legal'] = self.handle_contacts('legal')
			contacts = self.values.get('/spec/contacts');
			for name in contacts:
				r[name] = self.get_person(name)
		else:
			r['primary'] = primary
			
		
		self.values.set('/auto/contacts', r)
	
	def handle_contacts(self, type):
		contacts = self.values.get('/spec/contacts');
		r = {}
		for k, v in contacts.items():
			if v != type:
				continue
				
			person = self.get_person(k)
			if person is None:
				continue

			r[k] = person
		# print(r)
		return r if len(r) > 0 else None
		
	def get_partner(self, partnername):
		if partnername not in self.partner_contacts:
			logging.warning("Unknown partner %s" % partnername)
			return None
		return self.partner_contacts[partnername]

	def get_person(self, name):
		parts = name.split('-', 2)
		partnername = parts[0]
		personname = parts[1]

		partner = self.get_partner(partnername)
		if partner is None:
			return None

		if personname not in partner['members']:
			logging.warning("Unknown person %s of partner %s" % (personname, partnername))
			return None
		
		person = partner['members'][personname]
		person['company'] = partner['company']
		return person

	def handle_primary_contact(self):
		contacts = self.values.get('/spec/contacts');
		
		if 'primary' in contacts:
			return self.get_person(contacts['primary'])
		return None

	def fill_auto_values(self):
		auto = AutoValues(self.dw, self.pub, self.values)
		for k, v in auto.items():
			# print(k, v)
			self.values.set(k, v)
	
	def process_text_snippet(self, text):
		try:
			# print('a')
			text = self.rx_for.sub(self.handle_for, text)
			# print('b')
			text = self.rx_if.sub(self.handle_condition, text)
			# print('c')
			text = self.rx_value.sub(self.handle_value, text)
		except TypeError as e:
			print(text);
			print(e);
			text = ""
		return text

	rx_value = re.compile(r'\{\{(/[a-z\-/]+)\}\}')

	def handle_value(self, match):
		path = match.group(1)
		# print(path)
		val = self.values.get(path)
		if val is None:
			val = "[[UNDEFINED]]"
		# print(val)
		return self.process_text_snippet(val)
	
	rx_for = re.compile(r'\{\{for (/[a-z\-/]+)\}\}([ \t\f\v]*\n)?(.+?)\{\{endfor\}\}([ \t\f\v]*\n)?', re.DOTALL)

	def handle_for(self, match):
		# print(match.group())
		path = match.group(1)
		repl = match.group(3)
		# print(path)
		val = self.values.get(path)
		if val is None:
			return ""
		text = ""
		if type(val) is dict:
			val = val.values()
		for item in val:
			current = re.sub(r'%value(/[a-z0-9\-/]+)?%', lambda m: self.handle_item_value(item, m), repl)
			text += self.process_text_snippet(current)
		return text

	def handle_item_value(self, item, match):
		if len(match.group()) == 7:
			return str(item)
		path = match.group(1)
		# print(path)
		val = json_get(item, path)
		if val is None:
			val = "[[UNDEFINED]]"
		# print(val)
		return val

	rx_if = re.compile(r'\{\{if (/[a-z\-/]+) (!=|==) "([^\"]*)"\}\}([ \t\f\v]*\n)?(.+?)\{\{endif\}\}([ \t\f\v]*\n)?', re.DOTALL)

	def handle_condition(self, match):
		# print(match.group())
		path = match.group(1)
		op = match.group(2)
		compare = match.group(3)
		repl = match.group(5)

		val = self.values.get(path)
		if val is None:
			val = ""
		
		if op == '==' and val != compare:
			return ""
			
		if op == '!=' and val == compare:
			return ""

		return self.process_text_snippet(repl)

def list_all_meta_pages(dw):
	all_pages_info = dw.allpages()
	meta_pages = []
	
	for info in all_pages_info:
		fullname = dw.resolve(info['id'])
		if fullname is None:
			continue

		if mirror.rx_meta_pages.match(fullname) is None:
			continue
		
		meta_pages.append(fullname)
		
	return meta_pages

if __name__ == '__main__':
	import wikiconfig
	import sys
	
	# if len(sys.argv) < 2:
		# logging.info("Please provide the platform and enabler name as arguments")
		# sys.exit()
	
	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	pub_pages = mirror.public_pages(dw)
	pub = wikipublisher(dw, pub_pages, mirror.rx_exceptions, mirror.export_ns)
	
	with open('catalog-entry-template.txt', 'r') as template_file:
		template = template_file.read()
	
	cg = CatalogGenerator(dw, pub, template)
	
	meta_pages = list_all_meta_pages(dw)
	
	for metapage in meta_pages:
		logging.info("Start processing of meta page %s" % metapage)
		entry = None
		
		# metapage = ':ficontent:gaming:enabler:realitymixer:reflectionmapping:meta'
		meta = dw.getpage(metapage)
		metadata = preprocess.preprocess(meta)
		metajson = '\n'.join(metadata)
		
		try:
			se_spec = json.loads(metajson)
		except ValueError as e:
			logging.warning("Unable to read meta data from page %s. No valid JSON!\n%s" % (metapage, e))
			with open('_catalog/failed.meta' + re.sub(':', '.', metapage) + '.txt', 'w') as meta_file:
				meta_file.write(metajson)
			continue

		nc = NamingConventions(dw, se_spec)
		se_name = nc.fullname()
		
		if se_name not in releases.current[nc.roadmap()]:
			logging.info("Skip meta page of %s SE, because it is not part of the current release." % se_name)
			continue
		
		logging.info("Generating catalog entry for %s ..." % se_name)
		entry = cg.generate_entry(se_spec)
		
		np = nc.nameparts()
		
		with open('_catalog/catalog.' + '.'.join(np) + '.txt', 'w') as entry_file:
			entry_file.write(entry)
	
	
	logging.info("Finished")
