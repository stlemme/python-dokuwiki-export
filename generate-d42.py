#!/usr/bin/env python


from docxgenerate import *


if __name__ == '__main__':
	import wikiconfig

	templatefile = 'd42-template.docx'
	aggregatefile = 'd42-aggregate.txt'
	generatefile = 'd42-generated.docx'
	chapterfile = 'd42-chapters.txt'
	# imagepath = "media/"
	tocpage = ":ficontent:private:deliverables:d42:toc"
	deliverablepage = ":FIcontent.wiki.Deliverables.D42"
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
			re.compile(deliverablepage, re.IGNORECASE),
			re.compile("^:FIcontent.Gaming.Enabler.", re.IGNORECASE),
			re.compile("^:FIcontent.FIware.GE.Usage#", re.IGNORECASE),
		]
	)

	logging.info("Finished")

