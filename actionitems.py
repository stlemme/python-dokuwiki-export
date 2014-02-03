
import re
from wiki import *
import logging


class FixMe(object):
	def __init__(self, partner, todo, deadline, page, status = None):
		self.partner = partner
		self.todo = todo
		self.deadline = deadline
		self.page = page
		self.status = status
		
	def dump(self):
		deadline = self.deadline if self.deadline else ""
		status = self.status if self.status else ""
		return '| %s    | %s  | %s  | [[%s]]  |' % (self.partner, self.todo, deadline, self.page)

	rx_partner = r'([\w\-/,]+)'
	rx_deadline = r'([\w\-/, ]+)'
	rx_todo = (r'([^\n]+)', r'([^\|]+)')
	rx_page = r'\[\[([^\]]+)\]\]'
		
	rx_syntax = re.compile(r'FIXME[ ]+\[%s\][ ]+(\{%s\}[ ]+)?%s' % (rx_partner, rx_deadline, rx_todo[0]))
	rx_actionitem = re.compile(r'\|\s*%s\s*\|\s*%s\s*\|\s*%s\s*\|\s*%s\s*\|' % (rx_partner, rx_todo[1], rx_deadline, rx_page))
		
	@classmethod
	def parse(self, line):
		result = self.rx_actionitem.match(line)
		if result is None:
			return None
		return FixMe(result.group(0), result.group(1), result.group(2), result.group(3))

	
def collectfixmes(dw, ns):
	pages = dw.searchpages("FIXME")
	# print(pages)

	rx_namespace = re.compile(ns, re.IGNORECASE)
	
	pageids = [(dw.resolve(p['id']), p['score']) for p in pages]
	fixmes = []
	
	for pid, hits in pageids:
		if not rx_namespace.match(pid):
			continue
		
		doc = dw.getpage(pid)
		text = '\n'.join(doc)

		# print("Page: %s (%d)" % (pid, hits))
		matches = FixMe.rx_syntax.finditer(text)

		numfixmes = 0
		for f in matches:
			# print(f.group())
			numfixmes += 1
			partner = f.group(1)
			todo = f.group(4)
			deadline = f.group(3)
			
			# print("%s - %s\n%s" % (partner, deadline, todo))
			
			fixmes.append(FixMe(partner, todo, deadline, pid))
			
		if numfixmes != hits:
			logging.warning("Invalid FIXME syntax on page %s" % pid)

	import date
	fixmes.sort(key = lambda f: (date.parse(f.deadline), f.page))
	return fixmes

	
def parsefixmes(doc):
	preface = []
	fixmes = []
	postface = []

	ignore = preface
	
	for line in doc:
		f = FixMe.parse(line)
		if f is None:
			ignore.append(line)
			continue
		fixmes.append(f)
		ignore = postface
		
	return preface, fixmes, postface

	
def updateactionitems(dw, page, namespace):
	logging.info("Collecting FIXMEs in namespace %s" % namespace)
	fixmes = collectfixmes(dw, namespace)
	
	page = dw.resolve(page)
	# actions = PageBuffer(dw, outpage)
	
	# actions.write(dw.heading(1, "Action Items"))
	# actions.write('^ Partner ^ Todo ^ Deadline ^ Page ^')
	
	doc = dw.getpage(page)
	
	preface, actions, postface = parsefixmes(doc)
	
	# print(actions)
	# print()
	# print()
	# print(fixmes)
	
	result = preface
	
	for f in fixmes:
		result.append(f.dump())
	
	result.extend(postface)
	
	logging.info("Flushing action items to page %s" % page)
	dw.putpage(result, page)
	
	
if __name__ == "__main__":
	import sys
	import wikiconfig
	# from outbuffer import PageBuffer

	outpage = ":ficontent:private:action_items"
	namespace = ":ficontent:"

	if len(sys.argv) > 1:
		outpage = sys.argv[1]

	if len(sys.argv) > 2:
		namespace = sys.argv[2]

	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	# dw = wiki.DokuWikiLocal(url, 'pages', 'media')
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	updateactionitems(dw, outpage, namespace)

	logging.info("Finished")
