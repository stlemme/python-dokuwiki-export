
from . import Visitor


class ExperimentsVisitor(Visitor):
	def __init__(self, site = None, scenario = None):
		self.result = []
		self.site = site
		self.scenario = scenario
		
	def visit_Experiment(self, exp):
		if self.site is not None:
			if exp.get_site() != self.site:
				return

		if self.scenario is not None:
			if exp.get_scenario() != self.scenario:
				return
		
		self.result.append(exp)

	def get_result(self):
		return self.result

