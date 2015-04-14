
import logging
import re
from jsonutils import Values


class JsonGenerator(object):

	def __init__(self, escaping = lambda t : t):
		self.se = None
		self.escape = escaping
	
	def generate_entry(self, se):
		self.se = se
		
		entry = Values()
		
		nc = self.se.get_naming_conventions()

		entry.set('/id', nc.normalizedname())
		self.genDiscover(entry)
		self.genTry(entry)
		self.genTweak(entry)
		
		entry.set('/debug', self.se)

		self.se = None
		result = entry.serialize()
		if result is None:
			result = ""
		return result
	
	def genDiscover(self, entry):
		entry.set('/name', self.se.get_name())

		entry.set('/description/short', None)
		entry.set('/description/what-it-does', self.se.get('/spec/documentation/what-it-does'))
		entry.set('/description/how-it-works', self.se.get('/spec/documentation/how-it-works'))
		entry.set('/description/why-you-need-it', self.se.get('/spec/documentation/why-you-need-it'))

		entry.set('/categories/platforms', self.se.get('/spec/platforms'))
		entry.set('/categories/nice-platforms', self.se.get('/auto/nice-platforms'))
		entry.set('/categories/tags', None)
		entry.set('/categories/additional-tags', None)
		

	def genTry(self, entry):
		online_demo = self.se.get('/auto/usage/live-demo')
		entry.set('/try', online_demo)

	def genTweak(self, entry):
		playground_url = 'http://playground.simple-url.com:8000/'
		tweak = self.se.get('/auto/usage/playground/link')
		if tweak is not None:
			tweak = playground_url + tweak
		entry.set('/tweak', tweak)
