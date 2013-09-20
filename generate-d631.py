#!/usr/bin/env python


from generate import *


if __name__ == '__main__':

	templatefile = 'd631-template.docx'
	aggregatefile = 'd631-aggregate.txt'
	generatefile = 'd631-generated.docx'
	chapterfile = 'd631-chapters.txt'
	imagepath = "media/"
	wikiurl = "http://ficontent.dyndns.org/doku.php/"
	tocpage = "FIcontent.Wiki.Deliverables.D631.TOC"
	
	generatedoc(templatefile, generatefile, imagepath, tocpage, aggregatefile = aggregatefile, wikiurl=wikiurl)
