
import logging
from catalog import ThumbnailGenerator
from wiki import DokuWikiRemote


if __name__ == '__main__':
	import sys
	import wikiconfig
	
	filename = 'thumb.png'

	if len(sys.argv) < 2:
		sys.exit('Usage: %s :wiki:thumbnail.png [ thumb.png ]' % sys.argv[0])
	
	thumbname = sys.argv[1]
	
	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)

	thumbGen = ThumbnailGenerator(dw)
		
	if len(sys.argv) > 2:
		filename = sys.argv[2]

	thumbGen.generate_thumb(thumbname, filename)
