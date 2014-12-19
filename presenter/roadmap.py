
from . import PresenterBase
# import releases
# from entities import InvalidEntity
import wiki
import logging



class RoadmapPresenter(PresenterBase):
	def __init__(self, dw, roadmap, release):
		PresenterBase.__init__(self)
		self.dw = dw
		self.roadmap = roadmap
		self.release = release
		self.texts = {
			# 'what': "What you get",
			# 'why': "Why to get it",
			'what': 'What You Need',
			'why': 'Why You Need It',
			
			'doc': "Documentation",
			'wikipage': "Technical Documentation of the %s SE",
			'devguide': "Developer Guide of the %s SE",
			'new': " [NEW]"
		}
	
	def lookup_roadmap(self, se):
		nc = se.get_naming_conventions()
		roadmap = nc.roadmap()
		return roadmap
		
	def lookup_what(self, se):
		return se.get('/spec/documentation/what-it-does')

	def lookup_why(self, se):
		return se.get('/spec/documentation/why-you-need-it')

	def get_released_ses(self, releases):
		rel_ses = set()
		for rel in releases:
			rel_ses |= set(rel.get_specific_enablers())
		return list(rel_ses)

	def present(self, meta):
		rel_ses = self.release.get_specific_enablers() # self.get_released_ses(releases)

		rel_date = self.release.get_date()
		prev_releases = [rel for rel in meta.get_releases() if rel.get_date() < rel_date]
		prev_ses = self.get_released_ses(prev_releases)

		self.exploitation = []
		
		for se in rel_ses:
			if self.lookup_roadmap(se) != self.roadmap:
				continue
			
			if se not in rel_ses:
				continue
			
			nc = se.get_naming_conventions()
			
			se_name = se.get_name()
			se_what = self.lookup_what(se)
			se_why = self.lookup_why(se)

			se_wiki = nc.wikipage()
			se_devguide = nc.devguide()
			
			se_new = se not in prev_ses
			
			row = (se_name, se_what, se_why, se_wiki, se_devguide, se_new)
			self.exploitation.append(row)

	
	def dump(self, out):
		
		for se in self.exploitation:
			out << ''
			heading = se[0]
			if se[5]:
				heading += self.texts['new']
			out << self.dw.heading(3, heading)
			out << self.dw.heading(4, self.texts['what'])
			out << se[1]
			out << ''
			out << self.dw.heading(4, self.texts['why'])
			out << se[2]
			out << ''
			out << self.dw.heading(4, self.texts['doc'])
			out << '  * %s' % self.dw.link(se[3], None, self.texts['wikipage'] % se[0])
			if self.dw.pageexists(se[4]):
				out << '  * %s' % self.dw.link(se[4], None, self.texts['devguide'] % se[0])

