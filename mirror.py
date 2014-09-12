
# from aggregate import *
import sys
import wikiconfig
import logging
from wiki import *
from publisher import *
import re
import releases
from namingconventions import *


# rx_public_pages = [
	# re.compile(r'^:ficontent:(fiware:ge_usage|architecture)$', re.IGNORECASE),
	# re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):(architecture|roadmap:(start|release[0-9_]+|upcoming_releases)|deployment)$', re.IGNORECASE),
	# TODO: smartcity:portal, smartcity:overview, *:prototypes
	# re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):enabler:([\w]+:)?[\w]+:([\w]+)$', re.IGNORECASE),
	
	# media files
	# re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):([\w:]+:)?([^:]+\.(png|jpg))$', re.IGNORECASE),
	# re.compile(r'^:ficontent:([^:]+\.(png|jpg))$', re.IGNORECASE)
# ]

rx_meta_pages = re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):enabler:([\w]+:)?[\w]+:meta$', re.IGNORECASE)

rx_exceptions = [
	rx_meta_pages
]

export_ns = ['ficontent', 'publish']

def public_pages(dw):
	rx_public_pages = [
		re.compile(r'^:ficontent:(fiware:ge_usage|architecture)$', re.IGNORECASE),
		re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):(architecture|roadmap:(start|release[0-9_]+|upcoming_releases)|deployment)$', re.IGNORECASE),
		# TODO: smartcity:portal, smartcity:overview, *:prototypes
		# media files
		re.compile(r'^:ficontent:(socialtv|smartcity|gaming|common):([\w:]+:)?([^:]+\.(png|jpg))$', re.IGNORECASE),
		re.compile(r'^:ficontent:([^:]+\.(png|jpg))$', re.IGNORECASE)
	]
	
	for platform in releases.current:
		enablers = releases.current[platform]
		for se in enablers:
			se_spec = {
				'name': se,
				# TODO: workaround to fake common SE's platforms
				'platforms': [platform] if platform != 'common' else ['socialtv', 'smartcity', 'gaming']
			}
			
			nc = NamingConventions(dw, se_spec)
			rx = re.compile(r'^' + nc.wikinamespace() + '([\w]+)$', re.IGNORECASE)
			rx_public_pages.append(rx)
	
	return rx_public_pages


def publish_pages(dw, pages, export_ns = []):
	pub = wikipublisher(dw, public_pages(dw), rx_exceptions, export_ns)
	
	for p in pages:
		fullname = dw.resolve(p)
		newname = pub.public_page(fullname)
		
		if newname is None:
			logging.info("Skip %s" % fullname)
			continue

		# if fullname not in debug_pages:
			# continue

		logging.info("Publish %s\n     -> %s" % (fullname, newname))
		
		# print("DONE!")
		pub.publish(fullname, newname)

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

	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	logging.info("Connected to remote DokuWiki at %s" % wikiconfig.url)

	all_pages = list_all_public_pages(dw)
	all_pages.sort()

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
	
