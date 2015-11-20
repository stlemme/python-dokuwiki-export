#!/usr/bin/env python


import logging
from wiki import *
from jsonutils import Values
from fidoc import FIdoc
from catalog import ThumbnailGenerator, TemplatedGenerator, JsonGenerator
import appearance
from entities import SpecificEnabler
import htmlutils
import re


output_prefix = '_catalog/'


def debug_invalid_se(metapage, se):
	logging.warning("Skip SE %s with its meta page at %s, because it describes no valid SE." % (se.get_name(), metapage))
	metajson = se.get('/metajson')
	if metajson is None:
		return
	with open(output_prefix + 'failed.meta' + re.sub(':', '.', metapage) + '.txt', 'w') as meta_file:
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
	thgen = ThumbnailGenerator(dw)

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
		
		se_name = se.get_name()
		
		# se = fidoc.get_specific_enabler(metapage)
		if not se.is_valid():
			if se.get('/status') == 'deprecated':
				logging.info("Skip %s SE, because it is deprecated." % se_name)
				continue
			debug_invalid_se(se.get_metapage(), se)
			continue
		
		nc = se.get_naming_conventions()
		se_name = nc.fullname()
		
		if se not in rel_ses:
			logging.info("Skip %s SE, because it is not known as part of the current release." % se_name)
			continue
		
		if se.get('/sanity-check') != 'succeeded':
			logging.info("Skip %s SE, because it did not succeed the sanity checks." % se_name)
			continue

		entry_filename = output_prefix + 'catalog.' + nc.normalizedname()

		logging.info("Generating catalog entry for %s SE ..." % se_name)

		# catalog file
		# centry = cgen.generate_entry(se)
		# with open(entry_filename + '.txt', encoding='utf-8', mode='w') as entry_file:
			# entry_file.write(centry)
			
		# catalog output
		dentry = dgen.generate_entry(se)
		
		# thumbnail output
		thumbname = se.get('/auto/media/thumbnail')
		filename = output_prefix + dentry.get('/media/thumbnail')
		if not thgen.generate_thumb(thumbname, filename):
			logging.warning("Unable to create thumbnail for %s SE" % se_name)
			continue
		
		# write json file
		result = dentry.serialize()
		if result is None:
			logging.warning("Unable to serialize catalog entry for %s SE" % se_name)
			continue
	
		with open(entry_filename + '.json', encoding='utf-8', mode='w') as entry_file:
			entry_file.write(result)
		

	idx_playground = dgen.get_index('playground')
	with open(output_prefix + 'playground.json', encoding='utf-8', mode='w') as idx_file:
		idx_file.write(idx_playground)

	idx_tags = dgen.get_index('tags')
	with open(output_prefix + 'tags.json', encoding='utf-8', mode='w') as idx_file:
		idx_file.write(idx_tags)

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
