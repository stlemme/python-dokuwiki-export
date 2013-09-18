#!/usr/bin/env python


from docx import docx
from docxwrapper import *
from aggregate import *
from getpage import *


rx_line = {
	"heading": re.compile(r"^(=+) ([^=]+) (=+)$"),
	"image": re.compile(r"^[ ]*\{\{( *)([^\?\|\} ]+)(\?([^\|\} ]+))?( *)(\|([^\}]*))?\}\}$"),
	# "olist": re.compile(r"^([ ]{2,})\- (.*)$"),
	"ulist": re.compile(r"^([ ]{2,})\* (.*)$"),
	"empty": re.compile(r"^[ ]*$")
}


# rx_refimage = re.compile(r"^[ ]*<imgcaption ([^\|]+)\|([^>]+)>\{\{( *)([^\?\|\} ]+)(\?([^\|\} ]+))?( *)(\|([^\}]*))?\}\}</imgcaption>$")
rx_imageresize = re.compile(r"^([0-9]+)(x([0-9]+))?$")


rx_wiki_link = re.compile(r"\[\[([^\[\]\|]+)\|([^\[\]\|]+)\]\]")

rx_wiki_biu = [
	(re.compile(r"\*\*([^\*]+)\*\*"), 'b'),
	(re.compile(r"//([^/]+)//"), 'i'),
	(re.compile(r"__([^\*]+)__"), 'u'),
]

# rx_wiki_linebreak = re.compile(r"\s*\\\\\s*")


class wikiprocessor:
	def __init__(self, document, chapters, wikiurl):
		self.doc = document
		self.chapters = chapters
		self.wikiurl = wikiurl
	
	def replacelinks(self, c):
		if not "[[" in c:
			return c

		for m in rx_wiki_link.finditer(c):
			# print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
			found = m.group(0)
			s = found[2:-2].split('|')
			# name = s[0]
			target = m.group(1)
			caption = m.group(2)

			if target[:4] == "http":
				# external link
				repl = caption + u" (see " + target + u")"
			else:
				# internal link
				target = target.lower()
				if target in self.chapters:
					chapter, heading = self.chapters[target]
					if caption is None:
						caption = heading
					repl = caption + u" (see Section " + pretty_numbering(chapter) + u")"
				else:
					print "Unresolved Wiki Target:", target
					repl = caption + u" (refer to the FIcontent Wiki for more information)"
					# repl = caption + u" (available within the FIcontent Wiki at " + self.wikiurl + target + u")"
			# print found, name, repl, m.span()
			# t = t[:m.start()] + '___' + t[m.end():]
			c = c.replace(found, repl)

		return c



	def processwikitext(self, line):
		lineparts = [(line, '')]
		# return lineparts
		
		for rx, p in rx_wiki_biu:
			i = 0
					
			while i < len(lineparts):
				# print lineparts
				pt, pp = lineparts[i]
				
				# print "pt:", pt
				parts = rx.split(pt, 1)
				if len(parts) > 1:
					parts[0] = (parts[0], pp)
					parts[1] = (parts[1], pp+p)
					parts[2] = (parts[2], pp)
					# print parts
					
					lineparts[i:i+1] = parts
					# print lineparts
					# print
					i += 1			
				
				i += 1

		for i in xrange(len(lineparts)):
			pt, pp = lineparts[i]
			pt = self.replacelinks(pt)
			lineparts[i] = (pt, pp)

		return lineparts



	def ulistitem(self, line):
		# print line
		
		result = rx_line["ulist"].match(line)
		if result is not None:
			indent = len(result.group(1))
			level = indent / 2
			lineparts = self.processwikitext(result.group(2))
			return docx.paragraph(lineparts, style='EUListBullet1')
		else:
			return None
		
	
	def paragraph(self, line):
		lineparts = self.processwikitext(line)
		return docx.paragraph(lineparts, style='EUNormal')

	def heading(self, line):
		result = rx_line["heading"].match(line)
		if result is not None:
			indent1 = len(result.group(1))
			indent2 = len(result.group(3))
			if indent1 != indent2:
				print "Warning! Invalid heading."
			
			return docx.heading(result.group(2), 7-indent1)
		else:
			return None
			
	def insertimage(self, line):
		result = rx_line["image"].match(line)
		if result is not None:
			filename = result.group(2)
			fillleft = len(result.group(1)) > 0
			fillright = len(result.group(5)) > 0
			caption = result.group(7)
			imgwidth, imgheight = None, None
			
			if result.group(4) is not None:
				imgparams = result.group(4).split('&')
			
				for p in imgparams:
					result = rx_imageresize.match(p)
					if result is not None:
						# print result.groups()
						imgwidth = int(result.group(1))
						if result.group(3) is not None:
							imgheight = int(result.group(3))
				
			
			if filename[0:4] == "http":
				picfilename = filename.split('/')[-1]

				picfile = urllib2.urlopen(filename)
				print filename, '<------'
				print filename.split('/')[-1]
				output = open(join(imagepath, picfilename),'wb')
				output.write(picfile.read())
				output.close()
				filename = picfilename
			elif filename[0] == ":":
				filename = filename[1:]
			else:
				print "Invalid image file:", filename
				return

			if caption is None:
				caption = u"No caption available"
			
			print "Image:", filename, (imgwidth, imgheight)
			
			if filename[-3:] not in ["png", "jpg", "gif"]:
				print "Invalid image format!"
				return
			
			self.doc.insertpicture(filename, caption, (imgwidth, imgheight))


	def processlines(self, mode, lines):
		if mode is None:
			return None
		
		if len(lines) == 0:
			return None
		
		if mode == "heading":
			for l in lines:
				self.doc.insert(self.heading(l))
			return None
			
		if mode == "empty":
			return None
		
		if mode == "ulist":
			# items = ulist(lines)
			for l in lines:
				self.doc.insert(self.ulistitem(l))
			return None
			
		# elif mode == "olist":
			# doc.insert(olist(lines, doc))
		
		if mode == "image":
			for l in lines:
				self.insertimage(l)
			return None
			
		if mode == "text":
			for l in lines:
				self.doc.insert(self.paragraph(l))
			return None
			
		# elif mode == "table":
			# doc.insert(table(lines))

		if len(lines) > 0:
			print "Warning, parsing failed!", mode
			for l in lines:
				print l
			print
		

def generatedoc(templatefile, generatefile, imagepath, tocpage, aggregatefile=None, chapterfile=None, wikiurl=""):

	document = docxwrapper(templatefile, imagepath)

	toc = getpage(tocpage)
	if toc is None:
		sys.exit("Error! Table of Contents %s not found." % tocpage)

	doc, chapters = aggregate(toc)

	wp = wikiprocessor(document, chapters, wikiurl)
	
	if aggregatefile is not None:
		fo = open(aggregatefile, "w")
		fo.writelines(doc)
		fo.close()

	if chapterfile is not None:
		import json
		with open(chapterfile, 'w') as cf:
			json.dump(chapters, cf, sort_keys = False, indent = 4)

	
	# process aggregated document
	
	collectedlines = []
	lastline = None
	
	for line in doc:
		line = unicode(line, "utf-8")
		linetype = None
		
		for key, rx in rx_line.iteritems():
			result = rx.match(line)
			if result is not None:
				linetype = key
				break
		
		if linetype is None:
			linetype = "text"
		
		# print "linetype:", linetype
		
		if lastline != linetype:
			wp.processlines(lastline, collectedlines)
			collectedlines = []
			# print "Process lines:", lastline, " - ", len(collectedlines)
		
		lastline = linetype
		collectedlines.append(line)
	
	document.generate(generatefile)

