

import logging
from wiki import *
from namingconventions import *
from publisher import *
import re
from datetime import datetime
from urllib.parse import urlparse, parse_qs


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
				'devguide-url': self.pub_se_devguide_url
			},
			'delivery': {
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
				'youtube-pitch': self.pitch_id
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

	def pub_se_devguide_url(self):
		page = self.nc.devguide()
		info = self.dw.pageinfo(page)
		# print(page, info)
		if info is None:
			return None
		pub_page = self.pub.public_page(page)
		url = self.dw.pageurl(pub_page)
		# print(page, pub_page, url)
		return url

	def is_open_source(self):
		return self.YesNo(self.se.get('/spec/license/type') == 'open')
		
	def is_proprietary(self):
		return self.YesNo(self.se.get('/spec/license/type') == 'prop')

	def has_evaluation(self):
		return self.YesNo(self.se.get('/spec/license/type') == 'eval')

	def delivers_hosted_service(self):
		instances = self.se.get('/spec/delivery/instances')
		return self.YesNo((instances is not None) and (len(instances) > 0))
		
	def delivers_source_code(self):
		sources = self.se.get('/spec/delivery/source-code') is not None
		repo = self.se.get('/spec/delivery/repository') is not None
		return self.YesNo(sources or repo)
	
	def delivers_package(self):
		sources = self.se.get('/spec/delivery/sources') is not None
		binary = self.se.get('/spec/delivery/binary') is not None
		return self.YesNo(sources or binary)
	
	
	# rx_yt_link = re.compile(r'(?:youtube(?:-nocookie)?\.com/(?:[^/]+/.+/|(?:v|e(?:mbed)?)/|.*[?&]v=)|youtu\.be/)([^"&?/ ]{11})', re.IGNORECASE)
	
	def pitch_id(self):
		pitch = self.se.get('/spec/media/videos/pitch')
		if pitch is None:
			return None

		parts = urlparse(pitch)
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
		
	def timestamp(self):
		return str(datetime.now())
		
	def YesNo(self, cond):
		return 'Yes' if cond else 'No'
