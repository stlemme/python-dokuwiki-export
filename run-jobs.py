
import jobs
import logging
import datetime
from outbuffer import PageBuffer
from wiki import *
from fidoc import FIdoc


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

	job_list = []
	f = jobs.JobFactory()
	
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
		
		job_list.append(j)

	return job_list


def executejobs(fidoc, jobs, jobsuccess = None):
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
				success = j.perform(fidoc)
			except Exception as e:
				logging.fatal("Exception occured!\n%s" % e)
				
		except logging.FatalError:
			success = False
		
		if jobsuccess is not None:
			jobsuccess[j] = success
			
		overallsuccess &= success

		if not success:
			logging.error("JOB %d of %d: Aborted!" % (p, n))
			person = j.responsible(fidoc)
			if person is not None:
				logging.info("Notify %s about failed JOB %d" % (person, p))


def broadcastfailedjobs(failedjobs, fidoc):
	import notification
	
	# notifier = notification.MetaNotifier(dw, ':ficontent:private:meta:')
	# notifier = notification.UserFileNotifier(wikiconfig.userfile)
	
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
		person = fj.responsible(fidoc)
		if person is None:
			person = 'DFKI-Stefan'
		summary = fj.summary()
		# notifier.notify(
			# person,
			# subject % summary,
			# message % (person, summary)
		# )



if __name__ == "__main__":
	import sys
	import wikiconfig

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
	
	fidoc = FIdoc(dw)

	jobsuccess = {}
	
	try:
		overallsuccess = executejobs(fidoc, jobs, jobsuccess)
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
		broadcastfailedjobs(failedJobs, fidoc)
