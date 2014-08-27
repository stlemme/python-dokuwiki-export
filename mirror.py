
# from aggregate import *
import sys
import wikiconfig
import logging
from wiki import *
from publisher import *


rx_public_pages = [
	re.compile(r'^:ficontent:(fiware:ge_usage|architecture)$', re.IGNORECASE),
	re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):(architecture|roadmap:(start|release[0-9_]+|upcoming_releases)|deployment|.+\.(png|jpg))$', re.IGNORECASE),
	re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):enabler:([\w]+:)?[\w]+:(start|developerguide|.+\.(png|jpg))$', re.IGNORECASE)
]

rx_exceptions = [
]

export_ns = ['ficontent', 'publish']


def publish_pages(dw, pages, export_ns = []):
	pub = wikipublisher(dw, rx_public_pages, rx_exceptions, export_ns)
	
	for p in pages:
		fullname = dw.resolve(p)
		newname = pub.public_page(fullname)
		
		if newname is None:
			continue

		# if fullname not in debug_pages:
			# continue

		logging.info("Publish %s\n     -> %s" % (fullname, newname))
		
		# print("DONE!")
		pub.publish(fullname, newname)
	

if __name__ == "__main__":

	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	logging.info("Connected to remote DokuWiki at %s" % wikiconfig.url)


	all_pages_info = dw.allpages()
	all_pages = []
	
	for info in all_pages_info:
		p = dw.resolve(info['id'])
		if p is not None:
			all_pages.append(p)
	
	if len(sys.argv) > 1:
		pages = []
		
		for p in all_pages:
			for rx in sys.argv[1:]:
				if re.match(rx, p) is not None:
					pages.append(p)
					break
		
	else:
		pages = all_pages
		
	# print(pages)
		
	publish_pages(dw, pages, export_ns)

	logging.info("Finished!")
	
