#!/usr/bin/env python


from generate import *


if __name__ == '__main__':

	templatefile = 'd42-template.docx'
	generatefile = 'd42-generated.docx'
	chapterfile = 'd42-chapters.txt'
	imagepath = "media/"
	wikiurl = "http://ficontent.dyndns.org/doku.php?id="
	tocpage = "FIcontent.Wiki.Deliverables.D42"
	
	generatedoc(templatefile, generatefile, imagepath, tocpage, chapterfile=chapterfile, wikiurl=wikiurl)
