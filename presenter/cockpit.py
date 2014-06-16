
from presenter import PresenterBase
from visitor import SEVisitor
import re


class CockpitPresenter(PresenterBase):
	release0913 = {
		"socialtv": [
			"Audio Mining",
			"Audio Fingerprinting",
			"Content Optimisation",
			"Second Screen Framework",
			"TV Application Layer"
		],
		"smartcity": [
			"Local Information",
			"Recommendation Services",
			"Open City Database"
		],
		"gaming": [
			"Reality Mixer - Reflection Mapping",
			"Reality Mixer - Camera Artifact Rendering",
			"Leaderboard",
			"Augmented Reality - Fast Feature Tracking",
			"Augmented Reality - Marker Tracking",
			"Game Synchronization",
			"Spatial Matchmaking"
		],
		"common": [
			"Content Sharing",
			"Social Network",
			"Content Enrichment"
		]
	}
	
	products = {
		"Recommendation Services": "REPERIO",
		"Virtual/mixed Reality": "KIWANO",
		"Content Similarity": "Search & Discovery",
		"Content Atmosphere": "Search & Discovery"
	}
	
	url_exceptions = {
		"Audio Fingerprinting": "use-audio-fingerprinting",
		"Social Network": "social-network-enabler",
		"Content Sharing": "content-sharing",
		"Content Enrichment": "content-enrichment",
		"Open City Database": "open-city-database (missing)",
		"Local Information": "local-information (missing)",
		"Recommendation Services": "recommendation-services",
		"Audio Mining": "audio-mining",
		"Content Optimisation": "content-optimisation",
		"Second Screen Framework": "second-screen-framework",
		"TV Application Layer": "tv-application-layer",
		"Reality Mixer - Camera Artifact Rendering": "reality-mixer-camera-artefact-rendering-se (AE/BE conflict)"
	}
	
	def __init__(self, placeholder = "n/a"):
		PresenterBase.__init__(self)
		self.v = SEVisitor()
		self.placeholder = placeholder

	def lookup_product(self, id):
		if id in self.products:
			return self.products[id]
		
		return '-'
		
	def lookup_platform(self, id):
		for p, ses in self.release0913.items():
			if id in ses:
				return p
				
		return None
		
		
	def present(self, meta):
		self.v.visit(meta)
		
		self.exploitation = []
		for se in self.v.result:
			id = se.identifier
			product = self.lookup_product(id)
			platform = self.lookup_platform(id)
			owner = se.provider[0].identifier
			
			if platform is not None:
				cleanid = re.sub(r'[^\w\-]', '', id).replace('-', '.').lower()
				spec = 'http://wiki.mediafi.org/doku.php/ficontent.%s.enabler.%s' % (platform, cleanid)
				urlid = re.sub(r'\W+', '-', id).lower()
				#if id in self.url_exceptions:
				#	urlid = self.url_exceptions[id]
				catalog = 'http://mediafi.org/?portfolio=%s' % urlid
			else:
				spec = 'not yet released'
				catalog = 'not yet released'
			
			self.exploitation.append((
				se.identifier,
				product,
				owner,
				self.placeholder, # Open Source?
				self.placeholder, # FI-PPP mode
				'', # FI-PPP date
				'', # FI-PPP date
				self.placeholder, # FI-LAB mode
				'', # FI-LAB date
				'', # FI-LAB date
				self.placeholder, # others mode
				'', # others date
				spec,
				catalog
			))

		self.exploitation.sort(key = lambda tup: (tup[12], tup[0]))
		
	def dump(self, out):
		heading = [
			"availability for the FI-PPP partners",
			"availability within FI-LAB",
			"availability beyond the FI-PPP",
			"FI-PPP SEs",
			"SE implementation product(s) name(s) / owner",
			"",
			"Open Source (Yes/No/Planned)",
			"mode",
			"date last update",
			"date next / 1st update",
			"mode",
			"date last update",
			"date next / 1st update",
			"currently planned mode",
			"when",
			"Baseline assets",
			"Entry in Catalogue"
		]
		
		out.write('^ ^^^^ %s ^^^ %s ^^^ %s ^^ ^^' % tuple(heading[0:3]))
		out.write('^ %s ^' % (' ^ '.join(heading[3:])))
		
		for exp in self.exploitation:
			out.write('| %s | %s / %s | | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % exp)

