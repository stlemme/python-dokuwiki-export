#!/usr/bin/env python


from generate import *


if __name__ == '__main__':

	templatefile = 'd61-template.docx'
	generatefile = 'd61-generated.docx'
	imagepath = "media/"
	wikiurl = "http://ficontent.dyndns.org/doku.php?id="
	tocpage = "FIcontent.Wiki.Deliverables.D61"
	
	generatedoc(templatefile, generatefile, imagepath, tocpage, wikiurl=wikiurl)

	
