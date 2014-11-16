
from . import Entity


class Experiment(Entity):
	def __init__(self, site, date, conductor, place = None):
		self.site = site
		self.date = date
		self.conductor = conductor
		self.place = place
		self.scenario = None
		self.application = None
		self.deployments = {}

	def set_scenario(self, scenario, application):
		self.scenario = scenario
		self.application = application
	
	def set_enabler_location(self, enabler, location):
		if enabler in self.deployments:
			logging.warning("Ambiguous deployment information of %s during %s - using previous." % (enabler, self))
			return
		self.deployments[enabler] = location

	def __repr__(self):
		return "Experiment<%s, %s, %s>" % (self.site, self.date, self.conductor.get('name'))

	def get_site(self):
		return self.site
		
	def get_scenario(self):
		return self.scenario

	def get_application(self):
		return self.application
	
	def get_date(self):
		return self.date
