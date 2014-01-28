
# from aggregate import *
import sys
import wikiconfig
import logging
from wiki import *



def resolve_name(pagename, enabler):
	newname = pagename.replace('.', ':').replace(':ficontent:', ':ficontent:private:')
	
	if e:
		newname += ':'
	
	if newname == ':ficontent:private:fiware:ge:usage':
		newname = ':ficontent:private:fiware:ge_usage'
	
	return newname


def resolve_link(dw, ns, newns, page_map, match):
	page, section, text = dw.parselink(match.group())
	newname = None

	if page.startswith('http'):
		fullname = page
	else:
		oldns = []
		fullname = dw.resolve(page, ns, oldns)
		if fullname in page_map:
			mappedname = page_map[fullname]
			newname = dw.resolverel(mappedname, newns)
		
	# print(page)
	# print(fullname)
	# print(oldns)
	# print(newname)
	
	print("Resolve link %s -> %s" % (fullname, newname))
	
	if newname is not None:
		fullname = newname

	return dw.link(fullname, section, text)
	
	
def resolve_images(dw, ns, match):
	print(match.group())
	return match.group()
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


if __name__ == "__main__":

	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	logging.info("Connected to remote DokuWiki at %s" % wikiconfig.url)
	
	pages = dw.allpages()
	# print(pages)
	
	rx_pages = re.compile(r'^:ficontent\.(socialtv|smartcity|gaming|common|fiware)\.', re.IGNORECASE)
	rx_enablers = re.compile(r'^:ficontent\.(socialtv|smartcity|gaming|common)\.enabler\.[\w]+$', re.IGNORECASE)
	
	mirror_pages = {}
	
	for p in pages:
		fullname = dw.resolve(p['id'])
		m = rx_pages.match(fullname) is not None
		e = rx_enablers.match(fullname) is not None
		
		print("[%s] %s - %d" % (('M' if m else 'I'), fullname, p['size']))

		if not m:
			continue

		newname = resolve_name(fullname, e)
		fullnewname = dw.resolve(newname)
		mirror_pages[fullname] = fullnewname

	print()
	print()
	
	# debug
	debug_pages = [
		":ficontent.gaming.deployment",
		":ficontent.common.enabler.socialnetwork"
	]
	
	
	for op, np in [t for t in mirror_pages.items() if t[0] in debug_pages]:
		print("Copy %s\n  -> %s" % (op, np))
		
		pagens = []
		doc = dw.getpage(op, [], pagens)
		
		newns = []
		dw.resolve(np, [], newns)

		newdoc = []
		
		for line in doc:
			re1line = wiki.rx_link.sub(lambda m: resolve_link(dw, pagens, newns, mirror_pages, m), line)
			re2line = wiki.rx_image.sub(lambda m: resolve_images(dw, pagens, m), re1line)
			newdoc.append(re1line)

		dw.putpage(newdoc, np, summary='mirror page')
