
import logging
from jsonutils import Values
from . import ProcessingGenerator
import sanitychecks


class JsonGenerator(ProcessingGenerator):
	terms_template = '''
		<div class="terms-text">
			<div class="license summary">
				<p class="heading">Licence summary</p>
				<p class="content">{{/spec/license/summary}}</p>
			</div>
			<div class="license type">
				<p class="heading">Licence type</p>
				<ul class="content">
					<li>Open source: {{/auto/license/is-open-source}}</li>
					<li>Proprietary: {{/auto/license/is-proprietary}}</li>
					<li>Evaluation licence: {{/auto/license/has-evaluation}}</li>
				</ul>
			</div>
			<div class="license features">
				<p class="heading">Licence features</p>
				<ul class="content">
					<li>Commercial use: {{/spec/license/features/commercial-use}}</li>
					<li>Modifications allowed: {{/spec/license/features/modifications-allowed}}</li>
					<li>Distribution allowed: {{/spec/license/features/distribution-allowed}}</li>
					<li>Include copyright: {{/spec/license/features/include-copyright}}</li>
					<li>Include original: {{/spec/license/features/include-original}}</li>
					<li>State changes: {{/spec/license/features/state-changes}}</li>
					<li>Disclose source code: {{/spec/license/features/disclose}}</li>
				</ul>
			</div>
			<div class="license fee">
				<p class="heading">Licence fee</p>
				<p class="content">{{/spec/license/fee}}</p>
			</div>
			<div class="license copyright">
				<p class="heading">Copyright statement</p>
				<p class="content">{{/spec/license/copyright}}</p>
			</div>
			<div class="license full">
				<p class="heading">Full licence</p>
				<p class="content preformatted">{{/spec/license/full}}</p>
			</div>
		</div>'''
			
	contacts_template = '''
		<div class="contacts">
			<div class="owner">
				<p class="heading">Owner/developer</p>
				<p class="content">{{/auto/nice-owners}}</p>
			</div>
			<div class="persons">
				<p class="heading">Contact person(s)</p>
				{{if /auto/contacts/primary != ""}}
				<p class="person contact primary">
					<span class="name">{{/auto/contacts/primary/name}}</span>
					<span class="company">{{/auto/contacts/primary/company/fullname}}</span>
					<span class="email">{{/auto/contacts/primary/email}}</span>
				</p>
				{{endif}}

				{{if /auto/contacts/technical != ""}}
				<p class="subheading">For technical information:</p>

				{{for /auto/contacts/technical}}
				<p class="person contact technical">
					<span class="name">%value/name%</span>
					<span class="company">%value/company/fullname%</span>
					<span class="email">%value/email%</span>
				</p>

				{{endfor}}
				{{endif}}

				{{if /auto/contacts/legal != ""}}
				<p class="subheading">For licensing information:</p>

				{{for /auto/contacts/legal}}
				<p class="person contact legal">
					<span class="name">%value/name%</span>
					<span class="company">%value/company/fullname%</span>
					<span class="email">%value/email%</span>
				</p>

				{{endfor}}
				{{endif}}
			</div>
		</div>'''
			
	playground_url = 'http://playground.mediafi.org:8000/'

	def __init__(self, escaping = lambda t : t):
		ProcessingGenerator.__init__(self, escaping)
		self.idx = Values()

	
	def generate_entry(self, se):
		self.se = se
		
		entry = Values()
		
		nc = self.se.get_naming_conventions()
		self.se_id = nc.normalizedname()
		
		entry.set('/id', self.se_id)
		self.genDiscover(entry)
		self.genMedia(entry)
		self.genUsage(entry)
		self.genTermsAndConditions(entry)
		self.genDelivery(entry)
		
		# entry.set('/debug', self.se)
		
		self.se = None
		return entry
	

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
		entry.set('/terms/fi-ppp/text', self.process_text_snippet(self.terms_template))
		entry.set('/terms/fi-ppp/license/features', self.se.get('/spec/license/features'))
		entry.set('/terms/fi-ppp/license/type', self.se.get('/spec/license/type'))
		fields = ['summary', 'full', 'fee', 'copyright']
		for f in fields:
			entry.set('/terms/fi-ppp/license/' + f, self.process_value('/spec/license/' + f))
		
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
		entry.set('/category/nice-platforms', self.se.get('/auto/category/nice-platforms'))

		tags = self.se.get('/auto/category/tags')
		entry.set('/category/tags', tags)
		for t in tags:
			self.index('tags', t, self.se_id)

		tags = self.se.get('/auto/category/additional-tags')
		entry.set('/category/additional-tags', tags)
		for t in tags:
			self.index('additional-tags', t, self.se_id)
		
	def genDocumentation(self, entry):
		entry.set('/documentation/specification', self.se.get('/auto/documentation/wiki-url'))
		entry.set('/documentation/devguide', self.se.get('/auto/documentation/devguide-url'))
		entry.set('/documentation/installguide', self.se.get('/auto/documentation/installguide-url'))
		entry.set('/documentation/api', self.se.get('/auto/documentation/api-url'))
		additional = self.se.get('/auto/documentation/additional-resources')
		entry.set('/documentation/additional-resources', additional)
		if additional is None:
			return
		for url in additional:
			sanitychecks.check_remote_resource(url, 'Probably invalid link to additional resource!')
		
	def genSupport(self, entry):
		entry.set('/support/faq', self.se.get('/auto/support/faq-url'))
		entry.set('/support/bugtracker', self.se.get('/auto/support/bugtracker'))
		entry.set('/support/requests', None)
		entry.set('/support/contacts/text', self.process_text_snippet(self.contacts_template))
		
	
	
	def genYoutubeVideo(self, entry, json_path, yid):
		if yid is None:
			entry.set(json_path, None)
			return
		entry.set(json_path + '/youtube-id', yid)
		entry.set(json_path + '/url', 'https://youtu.be/%s' % yid)
	
	def genMedia(self, entry):
		filename = self.se.get('/auto/media/thumbnail')
		if filename is not None:
			fileparts = filename.rpartition(':')
			nc = self.se.get_naming_conventions()
			id = nc.normalizedname()
			entry.set('/media/thumbnail', 'catalog.%s.%s' % (id, fileparts[2]))
		else:
			entry.set('/media/thumbnail', None)
		self.genYoutubeVideo(entry, '/media/teaser', self.se.get('/auto/media/youtube-pitch'))
		self.genYoutubeVideo(entry, '/media/tutorial', self.se.get('/auto/media/youtube-tutorial'))
	
	def genTry(self, entry):
		online_demo = self.se.get('/auto/usage/online-demo')
		entry.set('/usage/try', online_demo)
		if online_demo is not None:
			sanitychecks.check_remote_resource(online_demo.get('/link'), 'Probably invalid try link!')
	
	def genTweak(self, entry):
		repo = self.se.get('/auto/usage/playground/link')
		if repo is not None:
			repoparts = repo.rpartition('/')
			suffix = repoparts[2]
			tweak = self.playground_url + suffix
			check = sanitychecks.check_remote_resource(repo + '/blob/master/playground.json', 'Probably invalid tweak link since no "playground.json" was found!')
			self.index('playground', suffix, {'url': repo, 'se': self.se.get_name(), 'valid': check})
		else:
			tweak = None
		entry.set('/usage/tweak', tweak)
		
	
	def genDelivery(self, entry):
		entry.set('/delivery/model', self.se.get('/auto/delivery/model'))
		entry.set('/delivery/artifact', self.process_value('/spec/delivery/description'))
		entry.set('/delivery/docker', self.se.get('/spec/delivery/docker'))
		entry.set('/delivery/saas-instance', self.se.get('/spec/delivery/instances/public/endpoint'))
		entry.set('/delivery/source-code', self.se.get('/spec/delivery/sources'))
		if self.se.get('/auto/delivery/repository/url') is None:
			entry.set('/delivery/repository', None)
		else:
			entry.set('/delivery/repository/url', self.se.get('/auto/delivery/repository/url'))
			entry.set('/delivery/repository/checkout-cmd', self.process_value('/auto/delivery/repository/checkout-cmd'))
	
	def index(self, idxname, key, val):
		path = '/' + idxname + '/' + key
		l = self.idx.get(path);
		if l is None:
			l = []
		l.append(val)
		self.idx.set(path, l)
	
	def get_index(self, idxname):
		idx = self.idx.get('/' + idxname)
		if idx is None:
			return ""
		result = idx.serialize()
		if result is None:
			return ""
		return result

