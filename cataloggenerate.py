#!/usr/bin/env python


import logging
from wiki import *
import re
from jsonutils import Values
from fidoc import FIdoc
from thumbnail import ThumbnailGenerator
import appearance
from entities import SpecificEnabler
import htmlutils


class CatalogGenerator(object):

	def __init__(self, template, escaping = lambda t : t):
		self.template = template
		self.se = None
		self.escape = escaping
	
	def generate_entry(self, se):
		self.se = se
		
		entry = self.template[:]
		
		# print(self.se.get('/auto'))
		# print(self.se.get('/spec'))

		entry = self.process_text_snippet(entry)
		self.se = None
		
		return entry
	
	stack = 0
	
	def process_text_snippet(self, text):
		# print('  ' * self.stack, text.encode('ascii', 'replace'))
		self.stack += 1
		
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
		self.stack -= 1
		return text

	rx_value = re.compile(r'\{\{(/[a-zA-Z\-/]+)\}\}')

	def handle_value(self, match):
		path = match.group(1)
		# print(path)
		val = self.se.get(path)
		if val is None:
			logging.warning('Undefined property %s' % path)
			val = "[[UNDEFINED]]"
		# print(val)
		val = self.escape(val)
		return self.process_text_snippet(val)
	
	rx_for = re.compile(r'\{\{for (/[a-zA-Z\-/]+)\}\}([ \t\f\v]*\n)?(.+?)\{\{endfor\}\}([ \t\f\v]*\n)?', re.DOTALL)

	def handle_for(self, match):
		# print(match.group())
		path = match.group(1)
		repl = match.group(3)
		# print(path)
		val = self.se.get(path)
		if val is None:
			return ""
		text = ""

		if isinstance(val, list):
			items = enumerate(val)
		else:
			items = val.items()

		for k, v in items:
			# print(k, '  --  ', v)
			current = re.sub(r'%value(/[a-zA-Z0-9\-/]+)?%', lambda m: self.handle_item_value(v, m), repl)
			text += self.process_text_snippet(current)
		
		return text

	def handle_item_value(self, item, match):
		if match.group() == '%value%':
			return str(item)
		path = match.group(1)
		# print(path)

		val = None
		if isinstance(item, Values):
			val = item.get(path)
		if isinstance(item, dict):
			val = item[path]

		if val is None:
			logging.warning('Undefined property %s of item' % path)
			val = "[[UNDEFINED]]"
		# print(val)
		val = self.escape(val)
		return val

	rx_if = re.compile(r'\{\{if (/[a-zA-Z\-/]+) (!=|==) "([^\"]*)"\}\}([ \t\f\v]*\n)?(.+?)\{\{endif\}\}([ \t\f\v]*\n)?', re.DOTALL)

	def handle_condition(self, match):
		# print(match.group())
		path = match.group(1)
		op = match.group(2)
		compare = match.group(3)
		repl = match.group(5)

		val = self.se.get(path)
		if val is None:
			val = ""
		
		if op == '==' and val != compare:
			return ""
			
		if op == '!=' and val == compare:
			return ""

		return self.process_text_snippet(repl)


def debug_invalid_se(metapage, se):
	logging.warning("Skip meta page of %s, because it describes no valid SE." % metapage)
	metajson = se.get('/metajson')
	if metajson is None:
		return
	with open('_catalog/failed.meta' + re.sub(':', '.', metapage) + '.txt', 'w') as meta_file:
		meta_file.write(metajson)

		
def generate_catalog(dw, template_filename, meta_pages = None):
	fidoc = FIdoc(dw)

	# with open(template_filename, 'r') as tmplfile:
		# template = tmplfile.read()
	templatefile = dw.getfile(template_filename)
	template = templatefile.decode("utf-8")
	# print(template)
	
	escaping = htmlutils.html_named_entity_escaping
	
	cgen = CatalogGenerator(template, escaping)
	thgen = ThumbnailGenerator()

	# if meta_pages is None:
		# meta_pages = fidoc.list_all_se_meta_pages()
		
	meta = fidoc.get_meta_structure()
	
	rel = meta.find_current_release()
	rel_ses = rel.get_specific_enablers()
	# print(rel_ses)
	
	# for metapage in meta_pages:
	for se in meta.get_specific_enablers():
		# logging.debug("Start processing of meta page %s" % metapage)
		entry = None

		# se = fidoc.get_specific_enabler(metapage)
		if not se.is_valid():
			debug_invalid_se(se.get_metapage(), se)
			continue
		
		nc = se.get_naming_conventions()
		se_name = nc.fullname()
		
		if se not in rel_ses:
			logging.info("Skip meta page of %s SE, because it is not known as part of the current release." % se_name)
			continue
		
		logging.info("Generating catalog entry for %s ..." % se_name)
		entry = cgen.generate_entry(se)
		
		np = nc.nameparts()
		
		entry_filename = '_catalog/catalog.' + '.'.join(np)
		
		with open(entry_filename + '.txt', encoding='utf-8', mode='w') as entry_file:
			entry_file.write(entry)
		
		bgcolor = appearance.select_bgcolor(se_name)
		
		thgen.generate_thumb(entry_filename + '.png', bgcolor, se_name)


	# logging.info("Dump invalid SE meta pages")
	# for se in meta.get_invalid_specific_enablers():
		# debug_invalid_se(se.get_metapage(), se)
	
	

if __name__ == '__main__':
	import wikiconfig
	import sys
	
	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	template_filename = 'ficontent:private:meta:catalog-entry-template.txt'
	# template_filename = 'catalog-entry-template.txt'
	
	meta_pages = None
	if len(sys.argv) > 1:
		meta_pages = sys.argv[1:]
	
	generate_catalog(dw, template_filename, meta_pages)
	logging.info("Finished")
