#!/usr/bin/env python


from docxgenerate import *


if __name__ == '__main__':
	import wikiconfig

	templatefile = 'd61-template.docx'
	aggregatefile = 'd61-aggregate.txt'
	generatefile = 'd61-generated.docx'
	chapterfile = 'd61-chapters.txt'
	# imagepath = "media/"
	tocpage = ":ficontent:private:deliverables:d61:toc"
	deliverablepage = ":ficontent:deliverables:d61"
	embedwikilinks = True

	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	# dw = wiki.DokuWikiLocal(url, 'pages', 'media')
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	logging.info("Generating docx file %s ..." % generatefile)
	
	desiredlinks = [
		re.compile(deliverablepage, re.IGNORECASE),
		re.compile("^:ficontent:(socialtv|smartcity|gaming|common):roadmap:(start)?(#.+)?$", re.IGNORECASE),
		re.compile("^:ficontent:(socialtv|smartcity|gaming|common):enabler:(.*):developerguide", re.IGNORECASE)
	]

	generatedoc(
		templatefile,
		generatefile,
		dw, tocpage,
		aggregatefile=aggregatefile,
		chapterfile=chapterfile,
		ignorepagelinks=desiredlinks
	)

	logging.info("Finished")
	
