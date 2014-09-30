#!/usr/bin/env python


import logging
from wiki import *
import re
import jsonutils
from fidoc import FIdoc


class CatalogGenerator(object):

	def __init__(self, template):
		self.template = template
		self.se = None
	
	def generate_entry(self, se):
		self.se = se
		
		entry = self.template
		
		entry = self.process_text_snippet(entry)
		self.se = None
		
		return entry
	
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
		val = self.se.get(path)
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
		val = self.se.get(path)
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
		val = jsonutils.json_get(item, path)
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

	templatefile = dw.getfile(template_filename)
	template = templatefile.decode("utf-8")
	# print(template)
	
	cgen = CatalogGenerator(template)
	
	if meta_pages is None:
		meta_pages = fidoc.list_all_se_meta_pages()
	
	for metapage in meta_pages:
		logging.info("Start processing of meta page %s" % metapage)
		entry = None

		se = fidoc.get_specific_enabler(metapage)
		if not se.is_valid():
			debug_invalid_se(metapage, se)
			continue
		
		nc = se.get_naming_conventions()
		se_name = nc.fullname()
		
		if se_name not in fidoc.get_current_release(nc.roadmap()):
			logging.info("Skip meta page of %s SE, because it is not part of the current release." % se_name)
			continue
		
		logging.info("Generating catalog entry for %s ..." % se_name)
		entry = cgen.generate_entry(se)
		
		np = nc.nameparts()
		
		with open('_catalog/catalog.' + '.'.join(np) + '.txt', 'w') as entry_file:
			entry_file.write(entry)
		

if __name__ == '__main__':
	import wikiconfig
	import sys
	
	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	template_filename = 'ficontent:private:meta:catalog-entry-template.txt'
	
	if len(sys.argv) > 1:
		meta_pages = sys.argv[1:]
	
	generate_catalog(dw, template_filename, meta_pages)
	logging.info("Finished")
