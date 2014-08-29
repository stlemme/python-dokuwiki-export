#!/usr/bin/env python


import logging
from wiki import *
import re
import json
from collections import deque
from publisher import *
import mirror
from catalogauto import *


def json_get(json_data, path):
	parts = deque(path[1:].split('/'))
	obj = json_data
	while len(parts) > 0:
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
		self.license_templates = {}
		with open('license-templates.json') as license_templates_file:
			self.license_templates = json.load(license_templates_file)
	
	
	def generate_entry(self, spec):
		self.values = Values({
			"spec": spec
		})
		self.fill_license()
		self.fill_auto_values()
		
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


	def fill_auto_values(self):
		auto = AutoValues(self.dw, self.pub, self.values)
		for k, v in auto.items():
			print(k, v)
			self.values.set(k, v)
	
	def process_text_snippet(self, text):
		text = self.rx_for.sub(self.handle_for, text)
		text = self.rx_if.sub(self.handle_condition, text)
		text = self.rx_value.sub(self.handle_value, text)
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


if __name__ == '__main__':
	import wikiconfig

	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	pub = wikipublisher(dw, mirror.rx_public_pages, mirror.rx_exceptions, mirror.export_ns)
	
	with open('catalog-entry-template.txt', 'r') as template_file:
		template = template_file.read()
	
	cg = CatalogGenerator(dw, pub, template)
	
	entry = None
	
	with open('realitymixer.reflectionmapping.meta.json', 'r') as se_spec_file:
		se_spec = json.load(se_spec_file)
		logging.info("Generating catalog entry for %s ..." % se_spec['name'])
		entry = cg.generate_entry(se_spec)
	
	# print(entry)
	
	with open('catalog.realitymixer.reflectionmapping.txt', 'w') as entry_file:
		entry_file.write(entry)
	
	logging.info("Finished")
