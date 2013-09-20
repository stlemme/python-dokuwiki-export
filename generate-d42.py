#!/usr/bin/env python


from generate import *


if __name__ == '__main__':

	templatefile = 'd42-template.docx'
	aggregatefile = 'd42-aggregate.txt'
	generatefile = 'd42-generated.docx'
	chapterfile = 'd42-chapters.txt'
	imagepath = "media/"
	wikiurl = "http://ficontent.dyndns.org/doku.php/"
	tocpage = "FIcontent.Wiki.Deliverables.D42.TOC"
	
	generatedoc(templatefile, generatefile, imagepath, tocpage, wikiurl=wikiurl, aggregatefile=aggregatefile)
