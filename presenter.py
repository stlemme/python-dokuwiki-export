
from visitor import ExperimentsVisitor
import dateutil.parser


def parsedate(date):
	return dateutil.parser.parse(date)

	
class ExperimentTimelinePresenter(object):
	def __init__(self, site = None):
		self.v = ExperimentsVisitor(site)
		
	def present(self, meta):
		self.v.visit(meta)
		self.experiments = [(exp.date, exp.site, exp.scenario) for exp in self.v.result]
		self.experiments.sort(key = lambda tup: (parsedate(tup[0]), tup[2]))
		
	def dump(self, out):
		out.write('^ Date  ^ Site  ^ Scenario ^\n')
		for exp in self.experiments:
			out.write('| %s    | %s    | %s       |\n' % exp)
		out.write('| ...   | ...   | ...      |\n')

