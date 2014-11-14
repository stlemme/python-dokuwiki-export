
from . import PresenterBase
from visitor import ExperimentsVisitor
import date


class ExperimentTimelinePresenter(PresenterBase):
	def __init__(self, site = None):
		PresenterBase.__init__(self)
		self.site = site
		self.v = ExperimentsVisitor(self.site)
		
	def present(self, meta):
		self.v.visit(meta)
		self.experiments = [(exp.get_date(), exp.get_site(), exp.get_scenario().get_name()) for exp in self.v.get_result()]
		self.experiments.sort(key = lambda tup: (date.parse(tup[0]), tup[2]))
		
	def dump(self, out):
		out.write('^ Date  ^ Site  ^ Scenario ^')
		for exp in self.experiments:
			out.write('| %s    | %s    | %s       |' % exp)
		# out.write('| ...   | ...   | ...      |')
