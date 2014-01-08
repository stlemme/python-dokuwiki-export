
# from getpage import *
from preprocess import *
from metaprocessor import *
import presenter
import wiki
import wikiconfig
import sys
from outbuffer import *
from visitor import *
import logging


def process_meta(meta):
	logging.info("Preprocessing page of meta structure ...")
	doc = preprocess(meta)
	
	data = MetaData(logging.warning, logging.error)
	
	mp = metaprocessor(data)
	logging.info("Processing meta structure ...")
	meta = mp.process(doc)

	if meta is None:
		logging.error("Meta structure corrupted.")
	
	return meta, data
	

def generate_page(dw, outpage, meta, data):	
	# out = FileBuffer(outfile)
	out = PageBuffer(dw, outpage)

	out << dw.heading(1, "Generated output from FIcontent's Meta-Structure")
	
	generated_content = [
		("Timeline of Experiments", presenter.ExperimentTimelinePresenter()),
		
	]
	
	
	sites = ["Zurich", "Brittany", "Lancaster", "Cologne", "Berlin", "Barcelona"]
	
	generated_content += [
		("Experiments in %s" % s, presenter.ExperimentTimelinePresenter(s)) for s in sites
	]
	
	
	scenarios = ["Immersive Control Systems", "Virtual Character Synchronization on the Web"]
	
	generated_content += [
		("Scenario %s" % s, presenter.DependencyPresenter(s)) for s in scenarios
	]
	
	
	id = lambda e: e.identifier
	ges = list(set(data.ge.values()))
	
	generated_content += [(
			"Utilization of %s GE" % ge.identifier,
			presenter.ListPresenter(UsedByVisitor(
				ge, experiment = False, transitive = True
			), id)
		) for ge in ges
	]
	
	
	for h, p in generated_content:
		logging.info('Generating -> "%s" ...' % h)
		p.present(meta)

		out << dw.heading(2, h)
		p.dump(out)
		out << ''
	
	logging.info("Flushing generated content ...")
	out.flush()

if __name__ == "__main__":
	
	metapage = ":FIcontent:private:meta:"
	if len(sys.argv) > 1:
		metapage = sys.argv[1]

	outfile = "generated-meta.txt"
	generatedpage = ":FIcontent:private:meta:generated"
	if len(sys.argv) > 2:
		outfile = sys.argv[2]


	logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	# dw = wiki.DokuWikiLocal(url, 'pages', 'media')
	dw = wiki.DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	logging.info("Loading page of meta structure %s ..." % metapage)
	metadoc = dw.getpage(metapage)
	if metadoc is None:
		logging.fatal("Meta structure %s not found." % metapage)

	meta, data = process_meta(metadoc)
	if meta is None:
		logging.fatal("Invalid meta structure %s." % metapage)
	
	generate_page(dw, generatedpage, meta, data)
	
	logging.info("Finished")
	
	