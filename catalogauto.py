

import logging
from wiki import *
from namingconventions import *
from publisher import *
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import sanitychecks


class AutoValues(object):
	def __init__(self, dw, pub, se):
		self.dw = dw
		self.pub = pub
		self.se = se
		self.nc = se.get_naming_conventions()
	
	def items(self):
		auto_values = {
			'documentation': {
				'wiki-url': self.pub_se_wiki_url,
				'devguide-url': self.pub_se_devguide_url,
				'installguide-url': self.pub_se_installguide_url,
				'api-url': self.pub_se_api_url,
				'additional-resources': self.additional_resources
			},
			'support': {
				'faq-url': self.pub_se_faq_url,
				'bugtracker': self.bugtracker_url
			},
			'delivery': {
				'model': self.delivery_model,
				'hosted-service': self.delivers_hosted_service,
				'source-code': self.delivers_source_code,
				'package': self.delivers_package,
				'repository': self.repository
			},
			'license': {
				'is-open-source': self.is_open_source,
				'is-proprietary': self.is_proprietary,
				'has-evaluation': self.has_evaluation
			},
			'media': {
				'youtube-pitch': self.pitch_id,
				'youtube-tutorial': self.tutorial_id,
				'thumbnail': self.thumbnail
			},
			'usage': {
				'online-demo': self.online_demo,
				'playground': self.playground,
				'tutorials': self.pub_se_tutorials_url
			},
			'category': {
				'tags': self.tags,
				'additional-tags': self.addtags,
				'nice-platforms': self.nice_platforms,
			},
			'timestamp': self.timestamp
		}
		
		items = {}
		self.process_auto_values(auto_values, '/auto', items)
		return items.items()

	def process_auto_values(self, obj, path, items):
		for k, v in obj.items():
			p = path + '/' + k
			if type(v) is dict:
				self.process_auto_values(v, p, items)
			else:
				# print(v)
				items[p] = v()
		
	def pub_se_wiki_url(self):
		page = self.nc.wikipage()
		pub_page = self.pub.public_page(page)
		return self.dw.pageurl(pub_page)

	def wiki_page_exists(self, page):
		info = self.dw.pageinfo(page)
		# print(page, info)
		return info is not None
		
	def wiki_pub_url(self, page):
		pub_page = self.pub.public_page(page)
		if pub_page is None:
			return None
		if not self.wiki_page_exists(pub_page):
			logging.warning("Referring to non-existent public wiki page %s" % pub_page)
			return None
		return self.dw.pageurl(pub_page)
	
	def pub_se_devguide_url(self):
		devguide = self.se.get('/spec/documentation/devguide')
		if devguide is not None:
			return devguide
		page = self.nc.devguide()
		if not self.wiki_page_exists(page):
			return None
		return self.wiki_pub_url(page)

	def pub_se_installguide_url(self):
		installguide = self.se.get('/spec/documentation/installguide')
		if installguide is not None:
			return installguide
		page = self.nc.installguide()
		if not self.wiki_page_exists(page):
			return None
		return self.wiki_pub_url(page)
		
	def pub_se_api_url(self):
		doxygen = self.se.get('/spec/documentation/api/doxygen')
		if doxygen is not None:
			return doxygen
		jsdoc = self.se.get('/spec/documentation/api/jsdoc')
		if jsdoc is not None:
			return jsdoc
		swagger = self.se.get('/spec/documentation/api/swagger')
		if swagger is None:
			swagger = 'http://fic2.github.io/swaggerfiles/%s/swagger.json' % self.nc.normalizedname()
		if sanitychecks.check_remote_resource(swagger, 'No swagger.json found!'):
			return '___SWAGGER___' + swagger
		return None
		
	def pub_se_faq_url(self):
		faq = self.se.get('/spec/support/faq')
		if faq is not None:
			return faq
		page = self.nc.faq()
		if not self.wiki_page_exists(page):
			return None
		return self.wiki_pub_url(page)

	def pub_se_tutorials_url(self):
		tut = self.se.get('/spec/examples/tutorials')
		if tut is not None:
			return tut
		page = self.nc.tutorials()
		if not self.wiki_page_exists(page):
			return None
		return self.wiki_pub_url(page)

	def additional_resources(self):
		additional = self.se.get('/spec/documentation/additional')
		if additional is None:
			return None
		
		return list(additional.values())

	def is_open_source(self):
		return self.YesNo(self.se.get('/spec/license/type') == 'open')
		
	def is_proprietary(self):
		return self.YesNo(self.se.get('/spec/license/type') == 'prop')

	def has_evaluation(self):
		return self.YesNo(self.se.get('/spec/license/type') == 'eval')

	def hosted_service_available(self, global_service=False):
		instances = self.se.get('/spec/delivery/instances')
		if instances is None:
			return False
		if not global_service:
			return len(instances) > 0
		return instances.get('/public/endpoint') is not None
	
	def delivers_hosted_service(self):
		return self.YesNo(self.hosted_service_available())
		
	def source_code_available(self):
		sources = self.se.get('/spec/delivery/source-code') is not None
		repo = self.se.get('/spec/delivery/repository') is not None
		return sources or repo
		
	def delivers_source_code(self):
		return self.YesNo(self.source_code_available())
	
	def binary_package_available(self):
		binary = self.se.get('/spec/delivery/binary')
		if binary is None:
			return False
		return len(binary) > 0
	
	def delivers_package(self):
		sources = self.se.get('/spec/delivery/sources') is not None
		binary = self.binary_package_available()
		return self.YesNo(sources or binary)
	
	def delivery_model(self):
		if self.source_code_available():
			return 'Source'
		if self.binary_package_available():
			return 'Binary'
		if self.hosted_service_available(global_service=True):
			return 'SaaS'
		logging.warning("Unknown delivery model for %s SE" % self.se.get_name())
		return 'Unknown'
	
	# rx_yt_link = re.compile(r'(?:youtube(?:-nocookie)?\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/ ]{11})', re.IGNORECASE)
	
	def youtube_id(self, value):
		if value is None:
			return None

		parts = urlparse(value)
		if parts.hostname == 'youtu.be':
			return parts.path[1:]
		if parts.hostname in ('www.youtube.com', 'youtube.com'):
			if parts.path == '/watch':
				p = parse_qs(parts.query)
				return p['v'][0]
			if parts.path[:7] == '/embed/':
				return parts.path.split('/')[2]
			if parts.path[:3] == '/v/':
				return parts.path.split('/')[2]
		return None
		
	def pitch_id(self):
		pitch = self.se.get('/spec/media/videos/pitch')
		return self.youtube_id(pitch)
	
	def tutorial_id(self):
		tutorial = self.se.get('/spec/media/videos/tutorial')
		return self.youtube_id(tutorial)
	
	def thumbnail(self):
		types = ['png', 'jpg']
		for t in types:
			file = self.nc.thumbnail(t)
			info = self.dw.fileinfo(file)
			# print(file)
			# print(info)
			if info is not None:
				return file
		# print(page, info)
		return None
	
	def repository(self):
		cmds = {
			'github': 'git clone --recursive {{/auto/delivery/repository/url}}.git',
			'git': 'git clone --recursive {{/auto/delivery/repository/url}}',
			'hg': 'hg clone {{/auto/delivery/repository/url}}',
			'svn': 'svn checkout {{/auto/delivery/repository/url}}'
		}
		repo = self.se.get('/spec/delivery/repository')
		if repo is not None:
			for k in cmds:
				if k not in repo:
					continue
				return {
					'url': repo[k],
					'checkout-cmd': cmds[k]
				}
		return {'url': None}
		
	def online_demo(self):
		return self.se.get('/spec/examples/live-demo')

	def playground(self):
		plexamples = self.se.get('/spec/examples/playground')
		if plexamples is None:
			return None
		if len(plexamples) > 0:
			return plexamples[0]
		return None
		
	def nice_platforms(self):
		plnames = []
		platforms = self.nc.platforms()
		if 'socialtv' in platforms:
			plnames.append('Social Connected TV')
		if 'smartcity' in platforms:
			plnames.append('Smart City Services')
		if 'gaming' in platforms:
			plnames.append('Pervasive Games')
		return plnames
		
	def tags(self):
		tags = self.se.get('/spec/tags')
		if tags is None:
			return []
		# invalidtags = set([t for t in tags if t not in sanitychecks.tags])
		# if len(invalidtags) > 0:
			# logging.warning('Invalid tags [%s] used! They are moved to additional tags.' % ', '.join(invalidtags))
		valtags = set(tags) & sanitychecks.tags
		if len(valtags) < len(tags):
			logging.warning('Invalid tags in use.')
		return list(valtags)
	
	def addtags(self):
		addtags = self.se.get('/spec/additional-tags')
		if addtags is None:
			addtags = []
		tags = self.se.get('/spec/tags')
		if tags is None:
			return addtags
		invalidtags = set(tags) - sanitychecks.tags
		if len(invalidtags) > 0:
			logging.warning('Invalid tags [%s] used! They are moved to additional tags.' % ', '.join(list(invalidtags)))
			addtags = list(set(addtags) | invalidtags)
		return addtags
		
	def bugtracker_url(self):
		tracker = self.se.get('/spec/support/bugtracker')
		if tracker is not None:
			return tracker
		repo = self.se.get('/spec/delivery/repository/github')
		if repo is not None:
			return repo + '/issues'
		return None
		
	def timestamp(self):
		return str(datetime.now())
		
	def YesNo(self, cond):
		return 'Yes' if cond else 'No'
