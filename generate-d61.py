#!/usr/bin/env python


from generate import *


if __name__ == '__main__':

	templatefile = 'd61-template.docx'
	aggregatefile = 'd61-aggregate.txt'
	generatefile = 'd61-generated.docx'
	imagepath = "media/"
	wikiurl = "http://ficontent.dyndns.org/doku.php/"
	tocpage = "FIcontent.Wiki.Deliverables.D61.TOC"
	
	desiredlinks = [
		re.compile(r"^FIcontent\.Gaming\.Roadmap#Pervasive_Games_Platform_\-_Upcoming_Releases", re.IGNORECASE),
		re.compile(r"^FIcontent\.Wiki\.Deliverables\.D61", re.IGNORECASE),
		re.compile(r"^FIcontent\.(SocialTV|SmartCity|Gaming|Common)\.Roadmap", re.IGNORECASE),
		re.compile(r"^FIcontent\.(SocialTV|SmartCity|Gaming|Common)\.Enabler\..*\.TermsandConditions", re.IGNORECASE),
		re.compile(r"^FIcontent\.(SocialTV|SmartCity|Gaming|Common)\.Enabler\..*\.DeveloperGuide", re.IGNORECASE)
	]
	
	generatedoc(
		templatefile, generatefile, imagepath, tocpage,
		aggregatefile = aggregatefile,
		wikiurl=wikiurl,
		ignorepagelinks=desiredlinks
	)

	
