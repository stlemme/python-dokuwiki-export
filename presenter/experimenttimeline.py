
from presenter import PresenterBase
from visitor import ExperimentsVisitor
import date


class ExperimentTimelinePresenter(PresenterBase):
	def __init__(self, site = None):
		PresenterBase.__init__(self)
		self.v = ExperimentsVisitor(site)
		
	def present(self, meta):
		self.v.visit(meta)
		self.experiments = [(exp.date, exp.site, exp.scenario) for exp in self.v.result]
		self.experiments.sort(key = lambda tup: (date.parse(tup[0]), tup[2]))
		
	def dump(self, out):
		out.write('^ Date  ^ Site  ^ Scenario ^')
		for exp in self.experiments:
			out.write('| %s    | %s    | %s       |' % exp)
		# out.write('| ...   | ...   | ...      |')
