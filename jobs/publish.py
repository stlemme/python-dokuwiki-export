
from . import Job
import mirror
import logging


class Publish(Job):
	def __init__(self, pages = None, export_ns = '', publisher = None):
		Job.__init__(self)
		self.pages = pages
		self.export_ns = export_ns
		self.publisher = publisher
	
	def summary(self):
		return "Publishing pages %s" % self.pages
	
	def required(self):
		return True

	def perform(self, fidoc):
		dw = fidoc.get_wiki()
		
		export_ns = []
		
		dw.resolve(self.export_ns, [], export_ns)
		logging.info("Export to namespace %s" % export_ns)
		# print(export_ns)
		# sys.exit()

		restpub = mirror.create_restrictedwikipublisher(fidoc, export_ns)
		
		pages = []

		if self.pages is not None:
			all_pages_info = dw.allpages()

			rx_pages = [re.compile(p) for p in self.pages]

			for info in all_pages_info:
				p = dw.resolve(info['id'])
				if p is None:
					continue
			
				for rx in rx_pages:
					if rx.match(p) is not None:
						pages.append(p)
						break
		else:
			# rx_pages = mirror.public_pages()
			pages = mirror.list_all_public_pages(dw, restpub)

		# print(pages)
		
		
		pages.sort()
		
		mirror.publish_pages(dw, restpub, pages, export_ns)

		logging.info("Finished!")
		return True
		
	def responsible(self, fidoc):
		return self.publisher

