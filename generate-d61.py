#!/usr/bin/env python


from generate import *


if __name__ == '__main__':

	templatefile = 'd61-template.docx'
	aggregatefile = 'd61-aggregate.txt'
	generatefile = 'd61-generated.docx'
	imagepath = "media/"
	wikiurl = "http://ficontent.dyndns.org/doku.php/"
	tocpage = "FIcontent.Wiki.Deliverables.D61.TOC"
	
	generatedoc(templatefile, generatefile, imagepath, tocpage, aggregatefile = aggregatefile, wikiurl=wikiurl)

	
