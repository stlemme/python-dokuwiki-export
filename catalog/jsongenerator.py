
import logging
from jsonutils import Values
from . import ProcessingGenerator


class JsonGenerator(ProcessingGenerator):
	terms_template = '''
		<div class="terms-text">
		<h2>Licence type</h2>
		<ul>
			<li>Open source: {{/auto/license/is-open-source}}</li>
			<li>Proprietary: {{/auto/license/is-proprietary}}</li>
			<li>Evaluation licence: {{/auto/license/has-evaluation}}</li>
		</ul>
		<h2>Licence features</h2>
		<ul>
			<li>Commercial use: {{/spec/license/features/commercial-use}}</li>
			<li>Modifications allowed: {{/spec/license/features/modifications-allowed}}</li>
			<li>Distribution allowed: {{/spec/license/features/distribution-allowed}}</li>
			<li>Include copyright: {{/spec/license/features/include-copyright}}</li>
			<li>Include original: {{/spec/license/features/include-original}}</li>
			<li>State changes: {{/spec/license/features/state-changes}}</li>
			<li>Disclose source code: {{/spec/license/features/disclose}}</li>
		</ul>
		<h2>Licence fee</h2>
		<p>{{/spec/license/fee}}</p>
		<h2>Licence summary</h2>
		<p>{{/spec/license/summary}}</p>
		<h2>Copyright statement</h2>
		<p>{{/spec/license/copyright}}</p>
		<h2>Full licence</h2>
		<p>{{/spec/license/full}}</p>
		</div>'''
			
	playground_url = 'http://playground.simple-url.com:8000/'

	def __init__(self, escaping = lambda t : t):
		ProcessingGenerator.__init__(self, escaping)

	
	def generate_entry(self, se):
		self.se = se
		
		entry = Values()
		
		nc = self.se.get_naming_conventions()

		entry.set('/id', nc.normalizedname())
		self.genDiscover(entry)
		self.genMedia(entry)
		self.genUsage(entry)
		self.genTermsAndConditions(entry)
		self.genDelivery(entry)
		
		entry.set('/debug', self.se)

		self.se = None
		result = entry.serialize()
		if result is None:
			result = ""
		return result
	
	def genDiscover(self, entry):
		entry.set('/name', self.se.get_name())
		entry.set('/supplier', self.process_value('/auto/nice-owners'))

		self.genDescription(entry)
		self.genCategory(entry)
		self.genDocumentation(entry)
		self.genSupport(entry)
		
	def genUsage(self, entry):
		self.genTry(entry)
		self.genTweak(entry)
		entry.set('/usage/tutorials', self.se.get('/auto/usage/tutorials'))
		
	def genTermsAndConditions(self, entry):
		entry.set('/terms/fi-ppp/type', self.se.get('/auto/license'))
		entry.set('/terms/fi-ppp/license', self.se.get('/spec/license'))
		entry.set('/terms/fi-ppp/text', self.process_text_snippet(JsonGenerator.terms_template))
		
		if self.se.get('/spec/license/beyond') is None:
			entry.set('/terms/beyond-fi-ppp', None)
			return
			
		# TODO: handle beyond FI-PPP license information
		
	def genDescription(self, entry):
		entry.set('/description/short', self.process_value('/spec/documentation/tag-line'))
		entry.set('/description/what-it-does', self.process_value('/spec/documentation/what-it-does'))
		entry.set('/description/how-it-works', self.process_value('/spec/documentation/how-it-works'))
		entry.set('/description/why-you-need-it', self.process_value('/spec/documentation/why-you-need-it'))

	def genCategory(self, entry):
		entry.set('/category/platforms', self.se.get('/spec/platforms'))
		entry.set('/category/nice-platforms', self.se.get('/auto/nice-platforms'))
		# TODO: handle and validate tags
		tags = []
		entry.set('/category/tags', tags)
		# TODO: handle and validate additional tags
		addtags = []
		entry.set('/category/additional-tags', addtags)
		
	def genDocumentation(self, entry):
		entry.set('/documentation/specification', self.se.get('/auto/documentation/wiki-url'))
		entry.set('/documentation/devguide', self.se.get('/auto/documentation/devguide-url'))
		entry.set('/documentation/installguide', self.se.get('/auto/documentation/installguide-url'))
		entry.set('/documentation/api', self.se.get('/auto/documentation/api-url'))
		
	def genSupport(self, entry):
		entry.set('/support/faq', self.se.get('/auto/support/faq-url'))
		entry.set('/support/bugtracker', self.se.get('/auto/support/bugtracker'))
		entry.set('/support/requests', None)
		entry.set('/support/contacts', self.se.get('/auto/contacts'))
		


	def genYoutubeVideo(self, entry, json_path, yid):
		if yid is None:
			entry.set(json_path, None)
			return
		entry.set(json_path + '/youtube-id', yid)
		entry.set(json_path + '/url', 'https://youtu.be/%s' % yid)
	
	def genMedia(self, entry):
		filename = self.se.get('/auto/media/thumbnail')
		fileparts = filename.rpartition(':')
		nc = self.se.get_naming_conventions()
		id = nc.normalizedname()
		entry.set('/media/thumbnail', 'catalog.%s.%s' % (id, fileparts[2]))
		
		self.genYoutubeVideo(entry, '/media/teaser', self.se.get('/auto/media/youtube-pitch'))
		self.genYoutubeVideo(entry, '/media/tutorial', self.se.get('/auto/media/youtube-tutorial'))

	def genTry(self, entry):
		online_demo = self.se.get('/auto/usage/online-demo')
		entry.set('/usage/try', online_demo)

	def genTweak(self, entry):
		repo = self.se.get('/auto/usage/playground/link')
		if repo is not None:
			repoparts = repo.rpartition('/')
			tweak = JsonGenerator.playground_url + repoparts[2]
		else:
			tweak = None
		entry.set('/usage/tweak', tweak)
		

	def genDelivery(self, entry):
		entry.set('/delivery/model', self.se.get('/auto/delivery/model'))
		entry.set('/delivery/artifact', self.process_value('/spec/delivery/description'))
		entry.set('/delivery/docker', self.se.get('/auto/delivery/docker'))
		entry.set('/delivery/saas-instance', self.se.get('/spec/delivery/instances/public/endpoint'))
		entry.set('/delivery/source-code', self.se.get('/spec/delivery/sources'))
		if self.se.get('/auto/delivery/repository') is None:
			entry.set('/delivery/repository', None)
		else:
			entry.set('/delivery/repository/url', self.se.get('/auto/delivery/repository/url'))
			entry.set('/delivery/repository/checkout-cmd', self.process_value('/auto/delivery/repository/checkout-cmd'))
	
	
		
		
		
		