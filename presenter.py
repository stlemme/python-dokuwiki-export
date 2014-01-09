

class Presenter(object):
	def present(self, meta):
		pass

	def dump(self, out):
		pass


from visitor import ExperimentsVisitor
import datetime
import dateutil.parser


def parsedate(date):
	try:
		dt = dateutil.parser.parse(date)
	except ValueError:
		dt = datetime.datetime(2997, 9, 12)
	return dt


class ExperimentTimelinePresenter(Presenter):
	def __init__(self, site = None):
		self.v = ExperimentsVisitor(site)
		
	def present(self, meta):
		self.v.visit(meta)
		self.experiments = [(exp.date, exp.site, exp.scenario) for exp in self.v.result]
		self.experiments.sort(key = lambda tup: (parsedate(tup[0]), tup[2]))
		
	def dump(self, out):
		out.write('^ Date  ^ Site  ^ Scenario ^')
		for exp in self.experiments:
			out.write('| %s    | %s    | %s       |' % exp)
		# out.write('| ...   | ...   | ...      |')


class ListPresenter(Presenter):
	def __init__(self, visitor, nice = lambda item: item):
		self.v = visitor
		self.nice = nice
		
	def present(self, meta):
		self.v.visit(meta)
		self.list = self.v.result
		
	def dump(self, out):
		for item in self.list:
			out.write('  * %s' % self.nice(item))


import re
from visitor import ExperimentsVisitor
from visitor import DependencyVisitor

class DependencyPresenter(Presenter):
	def __init__(self, scenario, site = None, relations = ['USES']):
		self.scenario = scenario
		self.site = site
		self.relations = relations
		
		self.ev = ExperimentsVisitor(site = self.site, scenario = self.scenario)
		self.dv = DependencyVisitor(self.relations)

		self.design = {
			'labeljust': 'left',
			'labelloc': 'top',
			'fontsize': 10,
			'APP_fillcolor': '#fff2cc',
			'APP_color': '#efbc00',
			'SE_fillcolor': '#deebf7',
			'SE_color': '#4a76ca',
			'GE_fillcolor': '#e2f0d9',
			'GE_color': '#548235',
			'EDGE_tailport': 's',
			'splines': 'line'
		}
		self.indent = '  '
		
	def present(self, meta):
		self.ev.visit(meta)
		# TODO: handle multiple apps per experiment
		self.apps = [exp.application for exp in self.ev.result]
		# print(self.apps)
		for a in self.apps:
			self.dv.visit(a)
		
	def dump_node(self, node):
		stripid = self.cleanid('%s_%s' % (node.entity, node.identifier))
		# print("%s -> %s" % (node.identifier, stripid))
		self.nodemap[node] = stripid
		self.dump_line('%s [label = "%s"];' % (stripid, node.identifier), indent=2)
		
	def dump_edge(self, node1, node2, edge):
		# App10913 -> GhiGE;
		id1 = self.nodemap[node1]
		id2 = self.nodemap[node2]
		# TODO: select appearance depending on edge
		self.dump_line('%s:%s -> %s [style = %s];' % (
				id1,
				self.lookup_design('tailport', ['EDGE_%s' % edge, 'EDGE']),
				id2,
				self.lookup_design('tailport', ['EDGE_%s' % edge, 'EDGE'])
			), indent=1)
		
	def dump_line(self, line, indent = 0):
		self.out.write(self.indent * indent + line)
		
	def cleanid(self, id):
		return re.sub(r'[^a-zA-Z_]+', '', id)
		
	def lookup_design(self, var, prefix):
		if not type(prefix) is list:
			prefix = [prefix]
		val = ['%s_%s' % (p, var) for p in prefix]
		for v in val:
			if v in self.design:
				return self.design[v]
		if var in self.design:
			return self.design[var]
		return None

	def dump_cluster(self, label, type):
		self.dump_line('subgraph cluster_%s {' % type, indent=1)
		self.dump_line('rank = same;', indent=2)
		self.dump_line('style = filled;', indent=2)
		self.dump_line('color = "%s";' % self.lookup_design('color', type), indent=2)
		self.dump_line('label = "%s";' % label, indent=2)
		self.dump_line('labeljust = %s;' % self.lookup_design('labeljust', type), indent=2)
		self.dump_line('labelloc = %s;' % self.lookup_design('labelloc', type), indent=2)
		self.dump_line('node [fillcolor = "%s"];' % self.lookup_design('fillcolor', type), indent=2)
		self.dump_line('')
		for n in [node for node in self.dv.nodes if node.entity == type]:
			self.dump_node(n)
		# self.dump_line('cluster_%s_DUMMY [style = invis, shape = point]' % type, indent=2)
		self.dump_line('};', indent=1)
		self.dump_line('')

		
	def dump(self, out):
		self.nodemap = {}
		self.out = out
		
		self.dump_line('<graphviz dot center>')
		self.dump_line('digraph scenario_%s {' % self.cleanid(self.scenario))
		self.dump_line('rankdir = TB;', indent=1)
		self.dump_line('compound = true;', indent=1)
		self.dump_line('outputorder = edgesfirst;', indent=2)
		self.dump_line('fontsize = %s;' % self.design['fontsize'], indent=1)
		self.dump_line('splines = %s;' % self.design['splines'], indent=1)
		self.dump_line('node [shape = box fontsize=%s style=filled fillcolor=grey];' % self.design['fontsize'], indent=1)
		self.dump_line('')
		
		self.dump_cluster('Applications', 'APP')
		self.dump_cluster('Specific Enablers', 'SE')
		self.dump_cluster('Generic Enablers', 'GE')

		for e in self.dv.edges:
			self.dump_edge(e[0], e[1], 'USES')
			
		# self.dump_line('cluster_APP_DUMMY -> cluster_SE_DUMMY [style = invis];')
		# self.dump_line('cluster_SE_DUMMY -> cluster_GE_DUMMY [style = invis];')
		
		self.dump_line('}')
		self.dump_line('</graphviz>')
		
		self.out = None
	
	