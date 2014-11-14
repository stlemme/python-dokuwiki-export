
from . import Visitor


class TestedScenariosVisitor(Visitor):
	def __init__(self, site = None):
		self.result = []
		self.site = site
		
	def visit_Experiment(self, exp):
		if self.site is not None:
			if exp.get_site() != self.site:
				return
		
		scenario = exp.get_scenario()
		if scenario in self.result:
			return
			
		self.result.append(scenario)
		
	def get_result(self):
		return self.result

