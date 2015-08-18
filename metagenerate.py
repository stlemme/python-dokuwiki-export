
from presenter import *
# , DependencyPresenter, GESurveyPresenter
import wiki
import sys
from outbuffer import *
from visitor import *
from entities import SpecificEnabler, DeprecatedSpecificEnabler, Application, PrettyPrinter
import logging
from fidoc import FIdoc



def generate_page(dw, outpage, meta):	
	# out = FileBuffer(outfile)
	out = PageBuffer(dw, outpage)

	out << dw.heading(1, "Generated output from FIcontent's Meta-Structure")
	
	generated_content = []
	
	pp = PrettyPrinter()

	
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
		("All Tested Scenarios", ListPresenter(TestedScenariosVisitor(), pp.print_Scenario)),
	]
	

	# All SEs and their relations
	#######################################
	
	generated_content += [(
			"Relations of %s SE" % se.get_name(),
			SEGraphPresenter(se, pp.dispatch)
		) for se in meta.get_specific_enablers()
	]
	
	# All SEs and their descriptions
	#######################################
	
	generated_content += [(
			"Description of %s SE" % se.get_name(),
			PropertyPresenter(se, '/spec/documentation/what-it-does')
		) for se in meta.get_specific_enablers()
	]

	# All SEs and their resources
	#######################################
	
	generated_content += [(
			"Resources of %s SE" % se.get_name(),
			ResourcesPresenter(dw, se, pp.dispatch)
		) for se in meta.get_specific_enablers()
	]

	# All SEs and their release cycle
	#######################################
	
	generated_content += [(
			"Release cycle of %s SE" % se.get_name(),
			ReleaseCyclePresenter(dw, se, pp.dispatch)
		) for se in meta.get_specific_enablers()
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
	
	generated_content += [(
			"Utilization of %s GE" % ge.get_name(),
			ListPresenter(UsedByVisitor(
				ge,
				follow_relations = ['USES'],
				collect_entities = [SpecificEnabler, DeprecatedSpecificEnabler, Application]
			), pp.dispatch)
		) for ge in meta.get_generic_enablers()
	]
	
	
	# Overall Uptake of Generic Enablers
	#######################################
	
	generated_content += [
		("Overall Uptake of Generic Enablers", UptakePresenter(pp.dispatch, hideunused=True))
	]
	
	
	# FI-PPP SEis Usage and General Information
	#######################################

	generated_content += [
		("FI-PPP SEis Usage and General Information", CockpitPresenter())
	]

	# SE Discovery Summary
	#######################################

	generated_content += [
		("SE Discovery Summary", SummaryPresenter())
	]

	# Incomplete/invalid SEis
	#######################################

	generated_content += [
		("Incomplete and/or invalid SEs", ListPresenter(InvalidEntitiesVisitor('SE'), pp.dispatch))
	]

	
	# GE Validation Survey
	#######################################

	# generated_content += [
		# ("GE Validation Survey", GESurveyPresenter())
	# ]
	
	# Roadmap Releases
	#######################################

	# releases = set([rel.get_name() for rel in meta.get_releases()])
	roadmaps = ['socialtv', 'smartcity', 'gaming', 'common']
	
	for rel in meta.get_releases():
		generated_content += [(
				"Roadmap %s - %s" % (road, rel.get_name()),
				RoadmapPresenter(dw, road, rel)
			) for road in roadmaps
		]

	
	#######################################
	# main generation loop
	#######################################
	
	for h, p in generated_content:
		logging.info('Generating -> %s ...' % h)
		p.present(meta)

		out << dw.heading(2, h)
		p.dump(out)
		out << ''
		
	logging.info("Flushing generated content ...")
	out.flush()



def generate_meta_information(fidoc, generatedpage):
	dw = fidoc.get_wiki()
	meta = fidoc.get_meta_structure()
	# pub = fidoc.get_publisher()
	
	if meta is None:
		logging.fatal("Invalid meta structure.")
	
	generate_page(dw, generatedpage, meta)
	
	
	
	
if __name__ == "__main__":
	
	import wikiconfig

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

		skipchecks = [
			# tv
			# 'Content Similarity', 'Audio Fingerprinting',
			# city
			# 'Local Information', 'Recommendation Services',
			# gaming
			# 'Visual Agent Design', 'Augmented Reality - Marker Tracking', 'Networked Virtual Character',
			# common
			# 'POI Storage', 'Content Sharing'
		]
		
		logging.info("Loading FIdoc object ...")
		fidoc = FIdoc(dw, skipchecks)
		
		generate_meta_information(fidoc, generatedpage)
		
		logging.info("Finished")
	
	except logging.FatalError:
		pass
		
