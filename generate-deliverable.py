#!/usr/bin/env python


from docxgenerate import *


if __name__ == '__main__':
	import wikiconfig
	import sys
	
	deliverable = 'd712'

	if len(sys.argv) > 1:
		deliverable = sys.argv[1]

	templatefile = deliverable + '-template.docx'
	aggregatefile = deliverable + '-aggregate.txt'
	generatefile = deliverable + '-generated.docx'
	chapterfile = deliverable + '-chapters.txt'
	# imagepath = "media/"
	tocpage = ":ficontent:private:deliverables:%s:toc" % deliverable
	# deliverablepage = ":FIcontent.wiki.Deliverables.D65"
	embedwikilinks = True

	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	# dw = wiki.DokuWikiLocal(url, 'pages', 'media')
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	logging.info("Generating docx file %s ..." % generatefile)
	generatedoc(
		templatefile,
		generatefile,
		dw, tocpage,
		aggregatefile=aggregatefile,
		chapterfile=chapterfile,
		ignorepagelinks=[
			# re.compile(deliverablepage, re.IGNORECASE),
			# re.compile("^:FIcontent.Gaming.Enabler.", re.IGNORECASE),
			# re.compile("^:FIcontent.FIware.GE.Usage#", re.IGNORECASE),
		]
	)

	logging.info("Finished")

