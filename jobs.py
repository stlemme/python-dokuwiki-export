
from aggregate import *
import sys
import wikiconfig
import logging
import datetime
from outbuffer import PageBuffer
import metagenerate
import actionitems
from docxgenerate import *
import mirror
from cataloggenerate import generate_catalog


class Job(object):
	def __init__(self):
		pass
		
	def summary(self):
		return "Unknown Job"

	def required(self):
		return False
		
	def perform(self, dw):
		return False
		
	def responsible(self, dw):
		return None
		

class Aggregation(Job):
	def __init__(self, tocpage, outpage, editor = None, embedwikilinks = True):
		Job.__init__(self)
		self.tocpage = tocpage
		self.outpage = outpage
		self.embedwikilinks = embedwikilinks
		self.editor = editor
	
	def summary(self):
		return "Aggregating %s" % self.tocpage
	
	def required(self):
		return True

	def perform(self, dw):
		logging.info("Loading table of contents %s ..." % self.tocpage)
		tocns = []
		toc = dw.getpage(self.tocpage, pagens = tocns)
		if toc is None:
			logging.error("Table of contents %s not found." % self.tocpage)
			return False
			
		logging.info("Aggregating pages ...")
		doc, chapters = aggregate(dw, toc, tocns, self.embedwikilinks)

		logging.info("Flushing generated content to page %s ..." % self.outpage)
		res = dw.putpage(doc, self.outpage)
		# print(res)
		# locks = dw.lockpage(self.outpage)
		# logging.info("Locks: %s" % locks)
		return res
		
	def responsible(self, dw):
		return self.editor

		
class MetaProcessing(Job):
	def __init__(self, metapage, outpage):
		Job.__init__(self)
		self.metapage = metapage
		self.outpage = outpage
	
	def summary(self):
		return "Regenerating output from meta structure at %s" % self.outpage
	
	def required(self):
		return True

	def perform(self, dw):
		metagenerate.generate_meta_information(dw, self.outpage)
		return True

	def responsible(self, dw):
		# TODO: retrieve last author of metapage
		info = dw.pageinfo(self.metapage)
		return info['author']


class UpdateActionItems(Job):
	def __init__(self, outpage, namespace = ':ficontent:', exceptions = []):
		Job.__init__(self)
		self.outpage = outpage
		self.namespace = namespace
		self.exceptions = exceptions
	
	def summary(self):
		return "Updating action items of namespace %s" % self.namespace
	
	def required(self):
		return True

	def perform(self, dw):
		actionitems.updateactionitems(dw, self.outpage, self.namespace, self.exceptions)
		return True

	def responsible(self, dw):
		return 'DFKI-Stefan'


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

	def perform(self, dw):
		# logging.info("Loading table of contents %s ..." % self.tocpage)
		# tocns = []
		# toc = dw.getpage(self.tocpage, pagens = tocns)
		# if toc is None:
			# logging.error("Table of contents %s not found." % self.tocpage)
			# return False
		
		# TODO: load template
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
			dw, self.tocpage,
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
		
	def responsible(self, dw):
		return self.editor

		
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

	def perform(self, dw):
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
			pages = mirror.list_all_public_pages(dw)

		# print(pages)
		
		export_ns = []
		
		dw.resolve(self.export_ns, [], export_ns)
		logging.info("Export to namespace %s" % export_ns)
		# print(export_ns)
		# sys.exit()
		
		pages.sort()
		
		mirror.publish_pages(dw, pages, export_ns)

		logging.info("Finished!")
		return True
		
	def responsible(self, dw):
		return self.publisher


class UpdateCatalog(Job):
	def __init__(self, template_filename = None, responsible = None):
		Job.__init__(self)
		self.template_filename = template_filename
		self.responsible = responsible
	
	def summary(self):
		return "Updating catalog with template file %s" % self.template_filename
	
	def required(self):
		return True

	def perform(self, dw):
		generate_catalog(dw, self.template_filename)
		logging.info("Finished!")
		return True
		
	def responsible(self, dw):
		return self.responsible

		
class JobFactory(object):
	jobs = {}
	
	def __init__(self):
		pass
		
	def create_job(self, jtype, params):
		jtype = jtype.lower()
		
		if jtype not in self.jobs:
			return None
		
		jclass = self.jobs[jtype]
		
		try:
			job = jclass(**params)
		except Exception as e:
			logging.error("Unable to create job instance - exception occurred!\n%s" % e)
			job = None
		
		return job

	@classmethod
	def register_job(self, jclass):
		self.jobs[jclass.__name__.lower()] = jclass

# jobs = [
	# MetaProcessing(":FIcontent:private:meta:", ":FIcontent:private:meta:generated"),
	# Aggregation(":ficontent:private:deliverables:d65:toc", ":ficontent:private:deliverables:d65:"),
	# Aggregation(":ficontent:private:deliverables:d42:toc", ":ficontent:private:deliverables:d42:", "stefan", False),
	# Aggregation(":ficontent:private:deliverables:d331:toc", ":ficontent:private:deliverables:d331:", "stefan_go")
# ]

# jobslog = ":ficontent:private:wikijobs.log"


class PageLog(PageBuffer):
	def __init__(self, wiki, page):
		PageBuffer.__init__(self, wiki, page)
		self.current = ""

	def write(self, text):
		lines = text.split('\n')
		self.current += lines[0]
		if len(lines) == 1:
			return
		
		for l in lines[1:-1]:
			PageBuffer.write(self, l)
		
		PageBuffer.write(self, self.current)
		self.current = lines[-1]
	
	def flush(self):
		PageBuffer.write(self, self.current)
		self.current = ""
		PageBuffer.flush(self)


def loadjobfile(jobfile):
	logging.info("Loading job file %s ..." % jobfile)

	try:
		import json
		with open(jobfile, 'r') as cf:
			jobdata = json.load(cf)
		return jobdata
	except Exception as e:
		logging.error("Unable to load job file - exception occurred!\n%s" % e)

	return None


def createjobs(jobdata):
	if jobdata is None:
		return []

	jobs = []
	f = JobFactory()
	
	for jname, jdata in jobdata["jobs"].items():
		# print(jname)
		# print(jdata)
		if jname == "inactive":
			continue
		
		if specificjobs is not None:
			if jname.lower() not in specificjobs:
				continue
		
		j = f.create_job(jdata["job"], jdata["params"])
		
		if j is None:
			logging.error("Unable to queue job '%s'." % jname)
			continue
		
		jobs.append(j)

	return jobs


def executejobs(jobs, jobsuccess = None):
	overallsuccess = True
	n = len(jobs)
	
	for i, j in enumerate(jobs):
		p = i+1
		logging.info("JOB %d of %d: %s" % (p, n, j.summary()))
		
		if not j.required():
			logging.info("Skipped!")
			continue
			
		try:
		
			try:
				success = j.perform(dw)
			except Exception as e:
				logging.fatal("Exception occured!\n%s" % e)
				
		except logging.FatalError:
			success = False
		
		if jobsuccess is not None:
			jobsuccess[j] = success
			
		overallsuccess &= success

		if not success:
			logging.error("JOB %d of %d: Aborted!" % (p, n))
			person = j.responsible(dw)
			if person is not None:
				logging.info("Notify %s about failed JOB %d" % (person, p))


def broadcastfailedjobs(failedjobs, dw):
	import notification
	
	# notifier = notification.MetaNotifier(dw, ':ficontent:private:meta:')
	notifier = notification.UserFileNotifier(wikiconfig.userfile)
	
	subject = 'Job failed: %s'
	message = '\n'.join([
		'Hello %s,'
		'',
		'your Job "%s" has failed during last execution.',
		'Please refer to the log at %s for errors and fix them as soon as possible.' % jobslog,
		'',
		'If you got stuck, please contact Stefan (stefan.lemme@dfki.de) or Dirk (dirk.krause@pixelpark.de).',
		'',
		'Best,'
		'\tdokuwikibot'
	])

	for fj in failedJobs:
		person = fj.responsible(dw)
		if person is None:
			person = 'DFKI-Stefan'
		summary = fj.summary()
		notifier.notify(
			person,
			subject % summary,
			message % (person, summary)
		)



if __name__ == "__main__":

	JobFactory.register_job(Aggregation)
	JobFactory.register_job(MetaProcessing)
	JobFactory.register_job(UpdateActionItems)
	JobFactory.register_job(WordGeneration)
	JobFactory.register_job(Publish)
	JobFactory.register_job(UpdateCatalog)
	
	if len(sys.argv) > 1:
		jobdata = loadjobfile(sys.argv[1])
			
	# print(jobdata)
	if len(sys.argv) > 2:
		specificjobs = [job.lower() for job in sys.argv[2:]]
	else:
		specificjobs = None


	if jobdata is not None:
		jobslog = jobdata["log"]
	else:
		jobslog = None

	
	jobs = createjobs(jobdata)
	
	dw = DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	log = PageLog(dw, jobslog)
	logging.out = log
	logging.cliplines = False
	
	log << dw.heading(1, "Log of dokuwikibot's jobs")
	log << "\n"
	log << "Latest run at %s" % datetime.datetime.now()
	log << "\n"
	log << "<code>"

	logging.info("Connected to remote DokuWiki at %s" % wikiconfig.url)

	jobsuccess = {}
	
	try:
		overallsuccess = executejobs(jobs, jobsuccess)
	except Exception as e:
		logging.error("Exception occured!\n%s" % e)
		overallsuccess = False

	logging.info("All done.")

	log << "\n"
	log << "</code>"
	log << "\n"

	log.flush()

	if not overallsuccess:
		failedJobs = [j for j in jobs if not ((j in jobsuccess) and (jobsuccess[j]))]
		print(failedJobs)
		broadcastfailedjobs(failedJobs, dw)
