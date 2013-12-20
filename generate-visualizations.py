
# from getpage import *
from preprocess import *
from metaprocessor import *
import presenter
import wiki
import wikiconfig
import sys
from outbuffer import *
from visitor import *
from logging import *



if __name__ == "__main__":
	
	metapage = ":FIcontent:private:meta:"
	if len(sys.argv) > 1:
		metapage = sys.argv[1]

	outfile = "generated-meta.txt"
	generatedpage = ":FIcontent:private:meta:generated"
	if len(sys.argv) > 2:
		outfile = sys.argv[2]


	info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
	# dw = wiki.DokuWikiLocal(url, 'pages', 'media')
	dw = wiki.DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
	
	info("Loading page of meta structure %s ..." % metapage)
	meta = dw.getpage(metapage)
	if meta is None:
		fatal("Meta structure %s not found." % metapage)

	info("Preprocessing page of meta structure ...")
	doc = preprocess(meta)
	
	data = MetaData(warning, error)
	
	mp = metaprocessor(data)
	info("Processing meta structure ...")
	meta = mp.process(doc)

	if meta is None:
		fatal("Meta structure corrupted.")
	
	# out = FileBuffer(outfile)
	out = PageBuffer(dw, generatedpage)

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
		info('Generating -> "%s" ...' % h)
		p.present(meta)

		out << dw.heading(2, h)
		p.dump(out)
		out << ''
	
	info("Flushing generated content ...")
	out.flush()
	
	info("Finished")
	
	