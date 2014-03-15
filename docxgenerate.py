#!/usr/bin/env python


from docx import docx
from docxwrapper import *
from aggregate import *
import logging
from wiki import *
import os
import urllib
import hashlib


rx_line = {
	"heading": wiki.rx_heading, # re.compile(r"^(=+) ([^=]+) (=+)$"),
	"image": re.compile(r"^[ ]*\{\{( *)([^\?\|\} ]+)(\?([^\|\} ]+))?( *)(\|([^\}]*))?\}\}$"),
	"olist": re.compile(r"^([ ]{2,})\- (.*)$"),
	"ulist": re.compile(r"^([ ]{2,})\* (.*)$"),
	"table": re.compile(r"^[\^\|]([^\^\|]*[\^\|])+$"),
	"code": re.compile(r"^<code.*>$"),
	"endcode": re.compile(r"^\s*</code.*>\s*$"),
	"graph": re.compile(r"^<graphviz(.*)>$"),
	"endgraph": re.compile(r"^</graphviz>$"),
	"fixme": re.compile(r"^FIXME .*$"),
	"empty": re.compile(r"^\s*$")
}


# rx_refimage = re.compile(r"^[ ]*<imgcaption ([^\|]+)\|([^>]+)>\{\{( *)([^\?\|\} ]+)(\?([^\|\} ]+))?( *)(\|([^\}]*))?\}\}</imgcaption>$")
rx_imageresize = re.compile(r"^([0-9]+)(x([0-9]+))?$")


rx_wiki_link = wiki.rx_link # re.compile(r"\[\[([^\[\]\|]+)\|([^\[\]\|]+)\]\]")

# rx_wiki_biu = [
	# (re.compile(r"\*\*([^\*]+)\*\*"), 'b'),
	# (re.compile(r"//([^/]+)//"), 'i'),
	# (re.compile(r"__([^_]+)__"), 'u'),
	# (re.compile(r"\s*([\\]{2})\s*"), 'n')
# ]

rx_wiki_biu = [
	('**', 'b'),
	('//', 'i'),
	('__', 'u'),
	('\\\\', 'n')
]

rx_wiki_table = re.compile(r"[\^\|]")
# rx_wiki_linebreak = re.compile(r"\s*\\\\\s*")


class wikiprocessor:
	def __init__(self, document, dw, ns, chapters, imagepath = "media/", ignore = []):
		self.doc = document
		self.dw = dw
		self.ns = ns
		self.chapters = chapters
		# self.wikiurl = wikiurl
		self.ignore = ignore
		self.imagepath = imagepath
	
	def resolve_link(self, match):
		page, section, caption = self.dw.parselink(match.group())

		# external link
		if page.startswith('http'):
			ref = self.doc.lookupref(page, page)
			return "%s [%d]" % (caption, ref)

		target = self.dw.resolve(page, self.ns)
		if section is not None:
			target += "#" + self.dw.target(section)
			
		target = target.lower()

		# internal link - contained within this document
		if target in self.chapters:
			chapter, heading = self.chapters[target]
			if caption is None:
				caption = heading
			return "%s (see Section %s)" % (caption, pretty_numbering(chapter))

		# internal link - not contained within this document -> refer to wiki
		ignore = False
		for p in self.ignore:
			if p.match(target) is not None:
				ignore = True
				break
		
		if not ignore:
			logging.info("Unresolved Wiki Target: %s" % target)
		
		ref = self.doc.lookupref(target, self.dw.pageurl(page, heading=section))
		return "%s [%d]" % (caption, ref)

		# repl = caption + u" (refer to the FIcontent Wiki for more information)"
		# repl = caption + u" (available within the FIcontent Wiki at " + self.wikiurl + target + u")"

	
	def replacelinks(self, c):
		if not "[[" in c:
			return c
		return wiki.rx_link.sub(self.resolve_link, c)
		

	def togglestyle(self, pp, p):
		if p in pp:
			return pp.replace(p, '')
		else:
			return pp + p


	def processwikitext(self, line):
		line = self.replacelinks(line)
		
		if "[[" in line:
			logging.warning("Missed links!")

		# debug
		# line = re.sub('[^\w:\+\._\-\(\)\\\, \*\/]+', '#', line)

		lineparts = [(line, '')]
		# return lineparts
		# print(lineparts)
		
		i = 0
		while i < len(lineparts):
			pt, pp = lineparts[i]

			first = (len(pt), None, None)
			
			for rx, p in rx_wiki_biu:
				parts = pt.split(rx, 1)
				if len(parts) == 1:
					continue
				pos = len(parts[0])
				if pos < first[0]:
					first = (pos, rx, p)
			
			rx = first[1]
			p = first[2]
			# print(first)

			# no style modifier in line part
			if rx is None:
				i += 1
				continue
			
			# split with first occurrence
			parts = pt.split(rx, 1)
			# print(parts)
			
			if p == 'n':
				lineparts[i:i+1] = [
					# leave the first part unchanged
					(parts[0].rstrip(), pp),
					# insert newline
					('', 'n'),
					# leave the second part unchanged
					(parts[1].lstrip(), pp)
				]
				i += 2

			else:
				lineparts[i:i+1] = [
					# leave the first part unchanged
					(parts[0], pp),
					# toggle style for second part
					(parts[1], self.togglestyle(pp, p))
				]
				i += 1
		
		# for rx, p in rx_wiki_biu:
			# i = 0
			
			# while i < len(lineparts):
				# print lineparts
				# pt, pp = lineparts[i]
				
				# print "pt:", pt
				# parts = rx.split(pt, 1)
				# if len(parts) > 1:
					# parts[0] = (parts[0], pp)
					# parts[1] = (parts[1], pp+p)
					# parts[2] = (parts[2], pp)
					# print parts
					
					# lineparts[i:i+1] = parts
					# print lineparts
					# print
					# i += 1          
				
				# i += 1

		# for i in xrange(len(lineparts)):
			# pt, pp = lineparts[i]
			# pt = self.replacelinks(pt)
			# lineparts[i] = (pt, pp)

		# print(lineparts)

		return lineparts

	def olistitem(self, line):
		# print line
		
		result = rx_line["olist"].match(line)
		if result is not None:
			indent = len(result.group(1))
			level = indent / 2
			lineparts = self.processwikitext(result.group(2))
			# return docx.paragraph(lineparts, style='EUListOrdered1')
			return docx.paragraph(lineparts, style='EUListBullet1')
		else:
			return None

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
		
	
	def paragraph(self, lines):
		parparts = []
		for l in lines:
			parparts += self.processwikitext(l)
		return docx.paragraph(parparts, style='EUNormal')

	def heading(self, line):
		heading, level = self.dw.parseheading(line)
		if heading is None:
			return None
		return docx.heading(heading, level)
		# result = rx_line["heading"].match(line)
		# if result is not None:
			# indent1 = len(result.group(1))
			# indent2 = len(result.group(3))
			# if indent1 != indent2:
				# print("Warning! Invalid heading.")
			
			# return docx.heading(result.group(2), 7-indent1)
		# else:
			# return None
			
	def insertimage(self, line):
		# return
		result = rx_line["image"].match(line)
		if result is None:
			return
			
		filename = result.group(2)
		fillleft = len(result.group(1)) > 0
		fillright = len(result.group(5)) > 0
		caption = result.group(7)
		imgwidth, imgheight = None, None
		
		# resizing
		if result.group(4) is not None:
			imgparams = result.group(4).split('&')
		
			for p in imgparams:
				result = rx_imageresize.match(p)
				if result is None:
					continue
				# print result.groups()
				imgwidth = int(result.group(1))
				if result.group(3) is not None:
					imgheight = int(result.group(3))

		if filename.startswith("http"):
			# referencing external image
			picfilename = filename.split('/')[-1]

			picfile = urllib2.urlopen(filename)
			logging.info('%s <------ web' % filename)
			data = picfile.read()
			# filename = picfilename
		
		else:
			# get file from wiki
			filename = self.dw.resolve(filename, self.ns)
			picfilename = filename.split(':')[-1]

			logging.info('%s <------ wiki' % filename)
			data = self.dw.getfile(filename)
			# filename = picfilename
		
		# unable to receive data
		if data is None:
			logging.warning("Invalid image file: %s" % filename)
			return

		# invalid file extension
		if not filename[-3:] in ['png', 'jpg', 'gif']:
			logging.warning("Invalid Media: %s" % filename)
			self.doc.insert(self.paragraph("FIXME Referencing media: " + filename))
			return

		# store cached image
		# print(picfilename)
		with open(os.path.join(self.imagepath, picfilename),'wb') as output:
			output.write(data)


			
		# print("Image:", filename, (imgwidth, imgheight))
		if caption is None:
			logging.info("No caption available for image %s" % filename)
			caption = "No caption available"
		
		
		jc = None
		
		if fillleft:
			jc = 'right'
		elif fillright:
			jc = 'left'
		if fillleft and fillright:
			jc = 'center'
		
		self.doc.insertpicture(picfilename, caption, (imgwidth, imgheight), jc)
		# self.doc.insert(self.paragraph('Image: %s with caption "%s" and params %s' % (filename, caption, (imgwidth, imgheight, jc))))

		
	def insertgraph(self, lines, align):
		gchapi = "https://chart.googleapis.com/chart"
		
		values = {
			'cht': 'gv',
			'chof': 'png',
			'chl': '\n'.join(lines)
		}
		data = urllib.parse.urlencode(values)
		data = data.encode('utf-8') # data should be bytes
		
		picfilename = 'graph-%s.png' % hashlib.md5(data).hexdigest()
		caption = None
		
		req = urllib.request.Request(gchapi, data)
		response = urllib.request.urlopen(req)
		imagedata = response.read()
		with open(os.path.join(self.imagepath, picfilename),'wb') as output:
			output.write(imagedata)
		
		self.doc.insertpicture(picfilename, caption, jc=align)

		return None


	def table(self, lines):
		rows = []
		# print "Table:"
		hasHeading = (lines[0][0] == '^')
		for l in lines:
			# print l
			cols = rx_wiki_table.split(l)
			cols = cols[1:-1]
			for i in range(len(cols)):
				cols[i] = self.paragraph([cols[i].strip()])
			# print cols
			rows.append(cols)
		# print
		# print
		psz = self.doc.pagecontentsize()
		return docx.table(
			rows,
			borders={'all': {'sz': 8, 'color': '000000', 'val': 'single'}},
			heading=hasHeading,
			tblw = int(1.0 * psz[0]),
			twunit = 'dxa',
			jc = 'center'
		)
		
	def pre(self, lines):
		return docx.paragraph(lines, style='EUCode')


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
		
		if mode == "fixme":
			# TODO: handle FIXMEs in a prominent way
			self.doc.insert(self.paragraph(["**%s**" % l for l in lines]))
			return None
			
		if mode == "ulist":
			# items = ulist(lines)
			for l in lines:
				self.doc.insert(self.ulistitem(l))
			return None
			
		elif mode == "olist":
			logging.warning("Ordered lists are not supported. Converted into unordered list ...")
			# doc.insert(olist(lines, doc))
			for l in lines:
				self.doc.insert(self.olistitem(l))
			return None
		
		if mode == "image":
			for l in lines:
				self.insertimage(l)
			return None
			
		if mode == "text":
			self.doc.insert(self.paragraph(lines))
			return None
			
		elif mode == "table":
			self.doc.insert(self.table(lines))
			return None
			
		elif mode == "code":
			# print "Code:"
			for l in lines[1:]:
				self.doc.insert(self.pre(l))
				# print l
			# print
			
			return None

		elif mode == "graph":
			# print("Graph:")
			# for l in lines[1:]:
				# self.doc.insert(self.pre(l))
				# print(l)
			# print
			self.insertgraph(lines[1:], 'center')
			
			return None

		if len(lines) > 0:
			print("Warning, parsing failed!", mode)
			for l in lines:
				print(l)
			print
		

def generatedoc(templatefile, generatefile, dw, tocpage, aggregatefile=None, chapterfile=None, injectrefs=False, ignorepagelinks=[], imagepath = "_media/"):

	document = docxwrapper(templatefile, imagepath)

	tocns = []
	toc = dw.getpage(tocpage, pagens = tocns)
	if toc is None:
		logging.fatal("Table of Contents %s not found." % tocpage)

	doc, chapters = aggregate(dw, toc, tocns, showwikiurl = injectrefs)
	
	# print()
	
	wp = wikiprocessor(document, dw, tocns, chapters, imagepath, ignorepagelinks)
	
	if aggregatefile is not None:
		with open(aggregatefile, "w") as fo:
			fo.writelines([l + '\n' for l in doc])

	if chapterfile is not None:
		import json
		with open(chapterfile, 'w') as cf:
			json.dump(chapters, cf, sort_keys = False, indent = 4)

	
	# process aggregated document
	
	collectedlines = []
	lastline = None
	
	for line in doc:
		# print(line)
		# line = unicode(line, "utf-8")
		linetype = None
		
		line = wp.replacelinks(line)
		
		for key, rx in rx_line.items():
			result = rx.match(line)
			if result is not None:
				linetype = key
				break
		
		# print "linetype1:", linetype

		if linetype is None:
			linetype = "text"

		if linetype == "endcode":
			linetype = "empty"
		elif lastline == "code":
			linetype = "code"

		if linetype == "endgraph":
			linetype = "empty"
		elif lastline == "graph":
			linetype = "graph"
		
		
		# print "linetype2:", linetype
		
		if lastline != linetype:
			try:
				wp.processlines(lastline, collectedlines)
				collectedlines = []
			except (Exception,UnicodeEncodeError) as e:
				print("Problem with lines!")
				for l in collectedlines:
					print(l)
					
				print()
				print(e)
				raise e
				break
			# print "Process lines:", lastline, " - ", len(collectedlines)
		
		lastline = linetype
		collectedlines.append(line)
	
	document.generate(generatefile)

