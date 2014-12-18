
from . import Entity


class Release(Entity):
	def __init__(self, platform, name):
		self.platform = platform
		self.name = name
		self.date = None
		self.enablers = []
		self.applications = []

	def set_date(self, date):
		self.date = date
	
	def add_app(self, app):
		self.applications.append(app)
		
	def add_se(self, se):
		self.enablers.append(se)


	def __repr__(self):
		return "Release<%s, %s>" % (self.platform, self.get_name())

	def get_platform(self):
		return self.platform
		
	def get_name(self):
		return "Release %s" % self.name

	def get_date(self):
		return self.date

	def get_applications(self):
		return self.applications
	
	def get_specific_enablers(self):
		return self.enablers
