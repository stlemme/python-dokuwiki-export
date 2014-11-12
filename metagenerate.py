
from presenter import ExperimentTimelinePresenter, ListPresenter, DependencyPresenter, UptakePresenter, CockpitPresenter, GESurveyPresenter
import wiki
import wikiconfig
import sys
from outbuffer import *
from visitor import *
import logging
from fidoc import FIdoc
from metaprocessor import MetaData


def generate_page(dw, outpage, meta):	
	# out = FileBuffer(outfile)
	out = PageBuffer(dw, outpage)

	out << dw.heading(1, "Generated output from FIcontent's Meta-Structure")
	
	generated_content = []
	
	
	meta_structure = meta.get_ast()
	meta_data = meta.get_data()

	# print(meta.ges)
	# print(meta.locations)
	# print(meta.scenarios)
	# print(meta.ses)
	# print(meta.apps)

	logging.seperator()
	for e in meta.edges:
		print(e)
	
	# Overall timeline of experiments
	#######################################
	
	generated_content += [
		("Timeline of Experiments", ExperimentTimelinePresenter()),
	]
	
	
	# Experiments per site
	#######################################
	
	sites = ["Zurich", "Brittany", "Lancaster", "Cologne", "Berlin", "Barcelona"]
	generated_content += [
		("Experiments in %s" % s, ExperimentTimelinePresenter(s)) for s in sites
	]

	
	# All tested scenarios
	#######################################
	
	generated_content += [
		("All Tested Scenarios", ListPresenter(ScenarioVisitor())),
	]
	
	
	# Dependencies per scenario
	#######################################
	
	# v = ExperimentsVisitor()
	# v.visit(meta_structure)
	
	# experiments = list(set([(e.scenario, e.site) for e in v.result]))
	
	# Dependencies per scenario (only actual usage)
	# generated_content += [
		# ('Scenario "%s" on Site %s - USES' % e, DependencyPresenter(e[0], e[1], ['USES'])) for e in experiments
	# ]

	# Dependencies per scenario (actual and planned usage)
	# relations = ['USES', 'WILL USE', 'MAY USE']
	# generated_content += [
		# ('Scenario "%s" on Site %s - ALL' % e, DependencyPresenter(e[0], e[1], relations)) for e in experiments
	# ]
	
	# Enablers used in experiments
	# niceenabler = lambda e: e.identifier + ' ' + e.entity
	
	# experiments = v.result # [e for e in v.result if (e.site == "Barcelona") and (e.application.identifier == "Smart City Guide (Android App)")]

	# generated_content += [(
			# 'Enablers tested in Scenario "%s" on Site %s at %s' % (e.scenario, e.site, e.date),
			# ListPresenter(
				# EnablersTestedVisitor(e.application, ts = e.date),
				# niceenabler
			# )
		# ) for e in experiments
	# ]
	

	# GE Utilization
	#######################################
	
	# TODO: step 2
	# id = lambda e: e.identifier
	# ges = list(set(meta_data.ge.values()))
	
	# generated_content += [(
			# "Utilization of %s GE" % ge.identifier,
			# ListPresenter(UsedByVisitor(
				# ge,
				# relations = ['USES'],
				# experiment = False
			# ), id)
		# ) for ge in ges
	# ]
	
	
	# Overall Uptake of Generic Enablers
	#######################################

	# csse = data.se['Content Sharing']
	# print('\nbla')
	# print(csse.usestates)
	
	# generated_content += [
		# ("Overall Uptake of Generic Enablers", UptakePresenter(hideunused=True))
	# ]
	
	# csse = data.se['Content Sharing']
	# print('\nblub')
	# print(csse.usestates)
	
	# FI-PPP SEis Usage and General Information
	#######################################

	# TODO: step 3
	# generated_content += [
		# ("FI-PPP SEis Usage and General Information", CockpitPresenter())
	# ]

	# GE Validation Survey
	#######################################

	# generated_content += [
		# ("GE Validation Survey", GESurveyPresenter())
	# ]
	
	#######################################
	# main generation loop
	#######################################
	
	for h, p in generated_content:
		logging.info('Generating -> %s ...' % h)
		p.present(meta_structure)

		out << dw.heading(2, h)
		p.dump(out)
		out << ''
		
		# csse3 = data.se['Content Sharing']
		# print('\nblub3:', h)
		# print(csse3.usestates)
		# if len(csse3.usestates['USES']) != len(csse.usestates['USES']):
			# print('DAMAGED!')

	
	# csse = data.se['Content Sharing']
	# print('\nblub2')
	# print(csse.usestates)

	logging.info("Flushing generated content ...")
	out.flush()



def generate_meta_information(dw, generatedpage):
	fidoc = FIdoc(dw)
	
	# meta_data = MetaData(logging.warning, logging.error)

	logging.info("Loading page of meta structure ...")
	meta = fidoc.get_meta_structure()
	
	if meta is None:
		logging.fatal("Invalid meta structure.")
	
	generate_page(dw, generatedpage, meta)

	
	
	
if __name__ == "__main__":
	
	metapage = ":FIcontent:private:meta:"
	if len(sys.argv) > 1:
		metapage = sys.argv[1]

	generatedpage = ":FIcontent:private:meta:generated"
	if len(sys.argv) > 2:
		generatedpage = sys.argv[2]

	try:

		logging.info("Connecting to remote DokuWiki at %s" % wikiconfig.url)
		# dw = wiki.DokuWikiLocal(url, 'pages', 'media')
		dw = wiki.DokuWikiRemote(wikiconfig.url, wikiconfig.user, wikiconfig.passwd)
		
		generate_meta_information(dw, generatedpage)
		
		logging.info("Finished")
	
	except logging.FatalError:
		pass
		
