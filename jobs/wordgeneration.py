
from . import Job
from docxgenerate import *
import logging


class WordGeneration(Job):
	def __init__(self, tocpage, templatefile, generatedfile, editor = None, injectrefs = True):
		Job.__init__(self)
		self.tocpage = tocpage
		self.templatefile = templatefile
		self.generatedfile = generatedfile
		self.injectrefs = injectrefs
		self.editor = editor
		self.docxpath = '_generated'
	
	def summary(self):
		return "Generating word document for %s" % self.tocpage
	
	def required(self):
		return True
	
	# rx_filename = re.compile(r".*:([\w\- \.]+)")
	# def filename(self, wikifilename):
		# if ':' not in wikifilename:
			# return wikifilename
		
		# result = self.rx_filename.match(wikifilename)
		# if result is None:
			# return None
		
		# return result.group(1)

	def perform(self, fidoc):
		dw = fidoc.get_wiki()
		# logging.info("Loading table of contents %s ..." % self.tocpage)
		# tocns = []
		# toc = dw.getpage(self.tocpage, pagens = tocns)
		# if toc is None:
			# logging.error("Table of contents %s not found." % self.tocpage)
			# return False
		
		templatefile = self.templatefile.split(':')[-1]
		generatedfile = self.generatedfile.split(':')[-1]
		
		data = dw.getfile(self.templatefile)
		
		# unable to receive data
		if data is None:
			logging.warning("Invalid template file: %s" % self.templatefile)
			return False

		with open(os.path.join(self.docxpath, templatefile), 'wb') as output:
			output.write(data)

			
		logging.info("Generating docx file %s ..." % generatedfile)
		generatedoc(
			os.path.join(self.docxpath, templatefile),
			os.path.join(self.docxpath, generatedfile),
			fidoc, self.tocpage,
			aggregatefile = None,
			chapterfile = None,
			injectrefs = self.injectrefs,
			ignorepagelinks=[
				# re.compile(deliverablepage, re.IGNORECASE),
				# re.compile("^:FIcontent.Gaming.Enabler.", re.IGNORECASE),
				# re.compile("^:FIcontent.FIware.GE.Usage#", re.IGNORECASE),
			],
			imagepath = '_media/'
		)
		
		# TODO: upload generated file
		
		return True
		
	def responsible(self, fidoc):
		return self.editor

