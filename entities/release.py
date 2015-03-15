
from . import Entity


class Release(Entity):
	def __init__(self, name):
		self.name = name
		self.date = None
		self.enablers = []

	def set_date(self, date):
		self.date = date

	def add_se(self, se):
		self.enablers.append(se)


	def __repr__(self):
		return "Release<%s>" % self.get_name()

	def get_name(self):
		return "Release %s" % self.name

	def get_date(self):
		return self.date

	def get_specific_enablers(self):
		return self.enablers

	def contains_se(self, se):
		return se in self.enablers
	