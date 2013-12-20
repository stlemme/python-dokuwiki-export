

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

class DependencyPresenter(Presenter):
	def __init__(self, scenario, site = None):
		self.v = ExperimentsVisitor(site = site, scenario = scenario)
		
	def present(self, meta):
		self.v.visit(meta)
		self.apps = [exp.application for exp in self.v.result]
		# print(self.apps)
		
	def dump_node(self, out, node):
		stripid = re.sub(r'[^a-zA-Z]+', '', node.identifier)
		# print("%s -> %s" % (node.identifier, stripid))
		self.nodemap[node] = stripid
		out.write('%s [label = "%s"];' % (stripid, node.identifier))
		
	def dump_edge(self, out, node1, node2, edge):
		# App10913 -> GhiGE;
		id1 = self.nodemap[node1]
		id2 = self.nodemap[node2]
		# TODO: select appearance depending on edge
		out.write('%s -> %s;' % (id1, id2))

	def dump(self, out):
		self.nodemap = {}
		out.write('<graphviz dot center>')
		out.write('digraph scenario_for_the_additional_report {')
		out.write('  rankdir=TB;')
		out.write('  node [shape = box fontsize=10 style=filled fillcolor=grey];')
		  
		out.write('subgraph cluster_applications {')
		out.write('  rank = same;')
		out.write('  style = filled;')
		out.write('  color = "#efbc00";')
		out.write('  node [fillcolor = "#fff2cc"];')
		
		for app in self.apps:
			self.dump_node(out, app)

		out.write('};')

		out.write('subgraph cluster_specific_enablers {')
		out.write('  rank = same;')
		out.write('  style = filled;')
		out.write('  color = "#4a76ca";')
		out.write('  node [fillcolor = "#deebf7"];')

		for app in self.apps:
			for se in [se for se in app.usestates['USES'] if se.entity == 'SE']:
				self.dump_node(out, se)

		out.write('};')

		out.write('subgraph cluster_generic_enablers {')
		out.write('  rank = same;')
		out.write('  style = filled;')
		out.write('  color = "#548235";')
		out.write('  node [fillcolor = "#e2f0d9"];')

		for app in self.apps:
			for ge in [ge for ge in app.usestates['USES'] if ge.entity == 'GE']:
				self.dump_node(out, ge)
				
		out.write('};')

		for app in self.apps:
			for e in app.usestates['USES']:
				self.dump_edge(out, app, e, 'USES')

		out.write('}')
		out.write('</graphviz>')
	
	
	