
import re
from wiki import *
import logging
from collections import deque


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

def resolve_link(dw, ns, match):
	page, section, text = dw.parselink(match.group())
	if page.startswith('http'):
		fullname = page
	else:
		fullname = dw.resolve(page, ns)
	return dw.link(fullname, section, text)
	
	
def resolve_images(dw, ns, match):
	# print(match.group())
	file, caption, params = dw.parseimage(match.group())
	# print(file, caption, params)
	if file.startswith('http'):
		fullname = file
	else:
		fullname = dw.resolve(file, ns)
	# print(fullname)
	image = dw.image(fullname, caption, params)
	# print(image)
	return image
	

rx_tocline = re.compile(r"^([ ]{2,})\- (.+)$")

def aggregate(dw, toc, tocns, showwikiurl = False):
	newdoc = []
	chapters = {}
	numbering = [0]
	
	pageheading = False
	
	for tocline in toc:
		result = rx_tocline.match(tocline)
		# print line
		# print result
		
		if result is None:
			continue
		
		# print result.groups()
		
		indent = result.group(1)
		item = result.group(2)
		
		level = int(len(indent) / 2)
		page, section, heading = dw.parselink(item)

		if page is None:
			increment_numbering(numbering, level)
			logging.info("%s - %s" % (pretty_numbering(numbering), heading))
			newdoc.append(dw.heading(level, item))
			continue

		pagens = []
		if section is not None:
			logging.warning("Ignoring section attribute of ToC. Including complete page %s instead." % page)
			# content = dw.getsection(page, section, tocns, pagens)
		# print level, page, "(", heading, ")"
		
		# append page with level offset
		# else:
		content = dw.getpage(page, tocns, pagens)
		
		# resolve page to full page name
		page = dw.resolve(page, pagens)

		if content is None:
			if heading is None:
				heading = "Missing page " + page
			content = []
			
		if heading is not None:
			increment_numbering(numbering, level)
			target = page
			chapters[target.lower()] = (numbering[:], heading)

			# logging.info("%s - %s" % (pretty_numbering(numbering), heading))

			newdoc.append(dw.heading(level, heading))
			# newdoc.append("\n")
			level += 1
			
			if showwikiurl:
				url = dw.pageurl(page)
				# print(url)
				newdoc.append("__ %s __" % url)
				newdoc.append("")
		else:
			pageheading = True
			
		contentQueue = deque(content)
		
		while len(contentQueue):
		
			line = contentQueue.popleft()
			
			# line is heading
			result = Wiki.rx_heading.match(line)
			if result is not None:
				# indent1 = len(result.group(1))
				# indent2 = len(result.group(3))
				# if indent1 != indent2:
					# logging.warning("Warning! Invalid heading.")
					
				# subleveloffset = 6 - indent1
				
				# subheading = result.group(2)
				subheading, subleveloffset = dw.parseheading(result.group())
				sublevel = level + (subleveloffset - 1)
				# logging.info('Aggregate section "%s" at sublevel = %s' % (subheading, sublevel))
				
				increment_numbering(numbering, sublevel)
				logging.info("%s - %s" % (pretty_numbering(numbering), subheading))
				
				target = page + "#" + dw.target(subheading)
				chapters[target.lower()] = (numbering[:], subheading)
				if pageheading:
					chapters[page.lower()] = (numbering[:], subheading)
					pageheading = False
				
				# logging.info("%s - %s" % (pretty_numbering(numbering), subheading))
				# print(pretty_numbering(numbering), " - ", subheading)
				
				newdoc.append(dw.heading(sublevel, subheading))

				if showwikiurl:
					url = dw.pageurl(page, heading=subheading)
					# print(url)
					# newdoc.append("")
					newdoc.append("__ %s __" % url)
					newdoc.append("")
					# newdoc.append("\n")
				
				continue
			
			# line is include
			result = Wiki.rx_include.match(line)
			if result is not None:
				# incpage = result.group(1)
				# incsection = result.group(3)
				incpage, incsection = dw.parseinclude(result.group())
				# newdoc.append("INCLUDE %s - %s\n" % (incpage, incsection))

				logging.debug('Aggregating include from %s of section "%s"' % (incpage, incsection))

				if "nightly" in incpage:
					secdoc = None
				else:
					# print(incpage, incsection, pagens, sublevel)
					incpagens = []
					secdoc = dw.getsection(incpage, incsection, pagens, incpagens, targetlevel=1)
				
				# print(secdoc)
				# print(contentQueue)

				if secdoc is None:
					logging.warning('Invalid include from %s of section "%s"' % (incpage, incsection))
					newdoc.append('INCLUDE %s - "%s" MISSING' % (incpage, incsection))
				else:
					# print(contentQueue)
					# print(secdoc)
					secdoc.reverse()
					# contentQueue.extendleft(secdoc)
					# incpage = dw.resolve(incpage, incpagens)
					for line in secdoc:
						re1line = Wiki.rx_link.sub(lambda m: resolve_link(dw, incpagens, m), line)
						re2line = Wiki.rx_image.sub(lambda m: resolve_images(dw, incpagens, m), re1line)
						contentQueue.appendleft(re2line)
				
				continue
			
			# line is usual content
			# resolve link namespaces
			re1line = Wiki.rx_link.sub(lambda m: resolve_link(dw, pagens, m), line)
			re2line = Wiki.rx_image.sub(lambda m: resolve_images(dw, pagens, m), re1line)
			newdoc.append(re2line)

		newdoc.append("")
		# newdoc.append("\n")
		
	return newdoc, chapters
		


if __name__ == "__main__":
	import sys
	import wikiconfig

	tocpage = ":ficontent:private:deliverables:d65:toc"
	if len(sys.argv) > 1:
		tocpage = sys.argv[1]

	outpage = ":ficontent:private:deliverables:d65:"
	if len(sys.argv) > 2:
		outpage = sys.argv[2]

	embedwikilinks = False
	if len(sys.argv) > 3:
		embedwikilinks = sys.argv[3] == 'embedlinks'

	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	# dw = wiki.DokuWikiLocal(url, 'pages', 'media')
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	logging.info("Loading table of contents %s ..." % tocpage)
	# toc = getpage(tocpage)
	tocns = []
	toc = dw.getpage(tocpage, pagens = tocns)
	if toc is None:
		logging.fatal("Table of contents %s not found." % tocpage)
		
	logging.info("Aggregating pages ...")
	doc, chapters = aggregate(dw, toc, tocns, embedwikilinks)

	logging.info("Flushing generated content to page %s ..." % outpage)
	dw.putpage(doc, outpage)

	if len(sys.argv) > 4:
		outfile = sys.argv[4]
		logging.info("Writing aggregated file %s ..." % outfile)

		with open(outfile, "w") as fo:
			fo.writelines([l + '\n' for l in doc])


	if len(sys.argv) > 5:
		chapterfile = sys.argv[5]
		logging.info("Writing chapter file %s ..." % chapterfile)

		import json
		with open(chapterfile, 'w') as cf:
			json.dump(chapters, cf, sort_keys = False, indent = 4)

	logging.info("Finished")
