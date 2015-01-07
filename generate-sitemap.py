
import sys
import wikiconfig
import logging
from wiki import *
from publisher import *
import mirror


def list_all_public_pages(dw):
	pub = wikipublisher(dw, public_pages(dw), rx_exceptions, export_ns)

	all_pages_info = dw.allpages()
	all_pages = []
	
	for info in all_pages_info:
		fullname = dw.resolve(info['id'])
		if fullname is None:
			continue

		newname = pub.public_page(fullname)
		if newname is None:
			continue
			
		all_pages.append(fullname)
		
	return all_pages

	
if __name__ == "__main__":
	logging.error("TODO: adapt source code")

	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	print("Connected to remote DokuWiki at %s" % wikiconfig.url)

	pub = wikipublisher(dw, mirror.public_pages(dw), mirror.rx_exceptions, mirror.export_ns)

	print("Generating sitemap ...")

	all_pages_info = dw.allpages()
	all_pages = [dw.resolve(info['id']) for info in all_pages_info]
	all_pages.sort()
	
	for fullname in all_pages:
		if fullname is None:
			continue

		newname = pub.public_page(fullname)
		p = 'X' if newname is not None else ' '
		
		print('[%s] %s' % (p, fullname))
		

	print("Finished!")
	