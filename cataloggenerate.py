#!/usr/bin/env python


import logging
from wiki import *
from jsonutils import Values
from fidoc import FIdoc
from catalog import ThumbnailGenerator, TemplatedGenerator, JsonGenerator
import appearance
from entities import SpecificEnabler
import htmlutils


def debug_invalid_se(metapage, se):
	logging.warning("Skip meta page of %s, because it describes no valid SE." % metapage)
	metajson = se.get('/metajson')
	if metajson is None:
		return
	with open('_catalog/failed.meta' + re.sub(':', '.', metapage) + '.txt', 'w') as meta_file:
		meta_file.write(metajson)

		
def generate_catalog(fidoc, template_filename, meta_pages = None):
	dw = fidoc.get_wiki()
	# with open(template_filename, 'r') as tmplfile:
		# template = tmplfile.read()
	templatefile = dw.getfile(template_filename)
	template = templatefile.decode("utf-8")
	# print(template)
	
	escaping = htmlutils.html_named_entity_escaping
	
	# cgen = TemplatedGenerator(template, escaping)
	dgen = JsonGenerator(escaping)
	# thgen = ThumbnailGenerator()

	# if meta_pages is None:
		# meta_pages = fidoc.list_all_se_meta_pages()
		
	meta = fidoc.get_meta_structure()
	if meta is None:
		logging.error("Unable to access meta structure");
		return
	
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
		
		entry_filename = '_catalog/catalog.' + nc.normalizedname()

		logging.info("Generating catalog entry for %s ..." % se_name)

		# catalog file
		# centry = cgen.generate_entry(se)
		# with open(entry_filename + '.txt', encoding='utf-8', mode='w') as entry_file:
			# entry_file.write(centry)
			
		# catalog file
		dentry = dgen.generate_entry(se)
		with open(entry_filename + '.json', encoding='utf-8', mode='w') as entry_file:
			entry_file.write(dentry)

		# thumbnail file
		# bgcolor = appearance.select_bgcolor(se_name)
		# thgen.generate_thumb(entry_filename + '.png', bgcolor, se_name)


	# logging.info("Dump invalid SE meta pages")
	# for se in meta.get_invalid_specific_enablers():
		# debug_invalid_se(se.get_metapage(), se)
	
	

if __name__ == '__main__':
	import wikiconfig
	import sys
	
	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)

	fidoc = FIdoc(dw)
	
	template_filename = 'ficontent:private:meta:catalog-entry-template.txt'
	# template_filename = 'catalog-entry-template.txt'
	
	meta_pages = None
	if len(sys.argv) > 1:
		meta_pages = sys.argv[1:]
	
	generate_catalog(fidoc, template_filename, meta_pages)
	logging.info("Finished")
