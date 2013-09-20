
import re
from getpage import *


def wikiheading(level, heading):
	return ("=" * (7 - level)) + " " + heading + " " + ("=" * (7 - level)) + "\n"


rx_link = re.compile(r"^\[\[([^\|\]]+)(\|([^\]]+))?\]\]$")

def parselink(link):
	result = rx_link.match(link)
	# print result.groups()
	target = result.group(1)
	text = result.group(3)
	return target, text

def increment_numbering(numbers, level):
	while len(numbers) < level:
		numbers.append(0)
	while len(numbers) > level:
		numbers.pop()
		
	numbers[level-1] += 1

def pretty_numbering(numbers):
	s = ""
	for n in numbers:
		s += str(n) + "."
	return s[:-1]

rx_tocline = re.compile(r"^([ ]{2,})\- (\[\[[^\|\]]+(\|[^\]]+)?\]\])")
rx_heading = re.compile(r"^(=+) ([^=]+) (=+)$")

def aggregate(toc, wikiurl=None):
	newdoc = []
	chapters = {}
	numbering = [0]
	
	for tocline in toc:
		result = rx_tocline.match(tocline)
		# print line
		# print result
		
		if result is None:
			continue
		
		# print result.groups()
		
		indent = result.group(1)
		link = result.group(2)
		
		level = len(indent) / 2
		page, heading = parselink(link)
		
		# print level, page, "(", heading, ")"
		
		# append page with level offset
		
		content = getpage(page)
		
		if content is None:
			if heading is None:
				heading = "Missing page " + page
			content = []
		
		if heading is not None:
			increment_numbering(numbering, level)
			target = page
			chapters[target.lower()] = (numbering[:], heading)

			print pretty_numbering(numbering), " - ", heading

			newdoc.append(wikiheading(level, heading))
			newdoc.append("\n")
			level += 1
			
			if wikiurl is not None:
				newdoc.append("__" + wikiurl + target + "__")
				newdoc.append("\n")
		
		for line in content:
			result = rx_heading.match(line)
			if result is None:
				newdoc.append(line)
				continue
				
			indent1 = len(result.group(1))
			indent2 = len(result.group(3))
			if indent1 != indent2:
				print "Warning! Invalid heading."
				
			subleveloffset = 6 - indent1
			
			sublevel = level + subleveloffset
			subheading = result.group(2)
			
			increment_numbering(numbering, sublevel)
			target = page + "#" + subheading.replace(" ", "_")
			chapters[target.lower()] = (numbering[:], subheading)

			print pretty_numbering(numbering), " - ", subheading
			
			newdoc.append(wikiheading(sublevel, subheading))

			if wikiurl is not None:
				newdoc.append("\n")
				newdoc.append("__" + wikiurl + target + "__")
				newdoc.append("\n")

		newdoc.append("\n")
		newdoc.append("\n")
		
	return newdoc, chapters
		


if __name__ == "__main__":
	import sys
	
	tocpage = "FIcontent.Wiki.Deliverables.D61"
	if len(sys.argv) > 1:
		tocpage = sys.argv[1]

	outfile = "generated-" + tocpage + ".txt"
	if len(sys.argv) > 2:
		outfile = sys.argv[2]

	toc = getpage(tocpage)
	if toc is None:
		sys.exit("Error! Table of Contents %s not found." % tocpage)

	doc, chapters = aggregate(toc)

	fo = open(outfile, "w")
	fo.writelines(doc)
	fo.close()

	if len(sys.argv) > 3:
		chapterfile = sys.argv[3]

		import json
		with open(chapterfile, 'w') as cf:
			json.dump(chapters, cf, sort_keys = False, indent = 4)
