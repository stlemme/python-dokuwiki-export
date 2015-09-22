
from jsonutils import Values
import logging


class Licenses(Values):
	def __init__(self, templates):
		if templates is None:
			logging.fatal("Missing license template information!")
		Values.__init__(self, templates)
		
		
	def process(self, license):
		if license is None:
			logging.warning("No license information available!")
			return license
		
		if 'template' not in license:
			return license
		
		template = self.get('/' + license.get('template'))
		if template is None:
			logging.warning("Invalid license template %s" % template)
			return license
		
		ovrlic = license
		# TODO: clone instance
		# license = dict(template)
		license = template.clone()
		# TODO: iterate over Values
		for k, v in ovrlic.items():
			license.set(k, v)
		
		return license
