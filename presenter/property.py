
from . import PresenterBase
from visitor import UsedByVisitor
from entities import SpecificEnabler, DeprecatedSpecificEnabler, Application


class PropertyPresenter(PresenterBase):
	def __init__(self, se, path):
		PresenterBase.__init__(self)
		self.se = se
		self.path = path

	def present(self, meta):
		self.description = self.se.get(self.path)
		
		if self.description is None:
			self.description = 'n/a'

	def dump(self, out):
		out.write(self.description)
