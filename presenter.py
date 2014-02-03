

class Presenter(object):
	def present(self, meta):
		pass

	def dump(self, out):
		pass

##############################################################################

from visitor import ExperimentsVisitor
import date


class ExperimentTimelinePresenter(Presenter):
	def __init__(self, site = None):
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

##############################################################################

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

##############################################################################

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
			'fontsize': 8,
			'APP_fillcolor': '#fff2cc',
			'APP_color': '#efbc00',
			'SE_fillcolor': '#deebf7',
			'SE_color': '#4a76ca',
			'GE_fillcolor': '#e2f0d9',
			'GE_color': '#548235',
			'EDGE_tailport': 's',
			'EDGE_color': '#000000',
			'EDGE_USES_style': 'solid',
			'EDGE_WILL_USE_style': 'dashed',
			'EDGE_MAY_USE_style': 'dashed',
			'EDGE_MAY_USE_color': '#838383',
			'splines': 'spline'
		}
		self.indent = '  '
		
	def present(self, meta):
		self.ev.visit(meta)
		# TODO: handle multiple apps per experiment
		self.apps = [exp.application for exp in self.ev.result]
		# print(self.apps)
		for a in self.apps:
			self.dv.visit(a)
		self.deployments = [exp.deployment for exp in self.ev.result]
		
		
	def dump_node(self, node, label = lambda node: node.identifier):
		stripid = self.cleanid('%s_%s' % (node.entity, node.identifier))
		# print("%s -> %s" % (node.identifier, stripid))
		self.nodemap[node] = stripid
		self.dump_line('%s [label = "%s"];' % (stripid, label(node)), indent=2)
		
	def dump_edge(self, node1, node2, edge):
		# App10913 -> GhiGE;
		id1 = self.nodemap[node1]
		id2 = self.nodemap[node2]
		# TODO: select appearance depending on edge
		edge = edge.replace(' ', '_')
		self.dump_line('%s:%s -> %s [style = %s, color = "%s"];' % (
				id1,
				self.lookup_design('tailport', ['EDGE_%s' % edge, 'EDGE']),
				id2,
				self.lookup_design('style', ['EDGE_%s' % edge, 'EDGE']),
				self.lookup_design('color', ['EDGE_%s' % edge, 'EDGE'])
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

	def dump_cluster(self, label, type, nodelabel = lambda node: node.identifier):
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
			self.dump_node(n, nodelabel)
		# self.dump_line('cluster_%s_DUMMY [style = invis, shape = point]' % type, indent=2)
		self.dump_line('};', indent=1)
		self.dump_line('')

	def lookup_deployment(self, enabler):
		locs = []
		for deployment in self.deployments:
			if enabler in deployment.keys():
				locs.append(deployment[enabler])
		if len(locs) == 0:
			self.fixmes.append('FIXME [Unknown] Provide deployment information for enabler "%s" in scenario "%s" on site %s' % (enabler.identifier, self.scenario, self.site))
			return "no deployment info"
		return ', '.join([l.identifier for l in set(locs)])
		

	def dump(self, out):
		self.nodemap = {}
		self.fixmes = []
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
		
		selabel = lambda node: '%s SE\\n(%s)' % (node.identifier, self.lookup_deployment(node))
		gelabel = lambda node: '%s GE\\n(%s)' % (node.identifier, self.lookup_deployment(node))
		
		self.dump_cluster('Applications', 'APP')
		self.dump_cluster('Specific Enablers', 'SE', nodelabel = selabel)
		self.dump_cluster('Generic Enablers', 'GE', nodelabel = gelabel)

		for e in self.dv.edges:
			self.dump_edge(e[0], e[1], e[2])
			
		# self.dump_line('cluster_APP_DUMMY -> cluster_SE_DUMMY [style = invis];')
		# self.dump_line('cluster_SE_DUMMY -> cluster_GE_DUMMY [style = invis];')
		
		self.dump_line('}')
		self.dump_line('</graphviz>')
		
		for f in self.fixmes:
			self.dump_line(f)
			self.dump_line('')
		
		self.out = None
	
##############################################################################

from visitor import GEVisitor, UsedByVisitor

class UptakePresenter(Presenter):
	def __init__(self, hideunused = False):
		self.v = GEVisitor()
		self.hideunused = hideunused

	def present(self, meta):
		self.v.visit(meta)
		self.uptake = []
		
		for ge in self.v.result:
			uv1 = UsedByVisitor(ge, 'USES', se=True, app=True, experiment=False, transitive=['USES'])
			uv1.visit(meta)
			uv2 = UsedByVisitor(ge, 'WILL USE', se=True, app=True, experiment=False, transitive=['USES', 'WILL USE'])
			uv2.visit(meta)
			uv3 = UsedByVisitor(ge, 'MAY USE', se=True, app=True, experiment=False, transitive=['USES', 'WILL USE', 'MAY USE'])
			uv3.visit(meta)

			if self.hideunused and len(uv1.result)+len(uv2.result)+len(uv3.result) == 0:
				continue
			self.uptake.append((ge, uv1.result, list(set(uv2.result)-set(uv1.result)), list(set(uv3.result)-set(uv1.result))))

		# self.experiments.sort(key = lambda tup: (parsedate(tup[0]), tup[2]))
		
	def dump(self, out):
		out.write('^ GE  ^  Uptake  ^ SEs ^')
		for ge, uses, will, may in self.uptake:
			ses = ['%s SE' % e.identifier for e in uses if e.entity == 'SE']
			apps = ['%s' % e.identifier for e in uses if e.entity == 'APP']

			wses = ['//%s SE//' % e.identifier for e in will + may if e.entity == 'SE']
			wapps = ['//%s//' % e.identifier for e in will + may if e.entity == 'APP']

			uptake = ' \\\\ '.join(ses + apps + wses + wapps)
			
			if len(uses):
				status = 'D'
			elif len(will):
				status = 'U'
			elif len(may):
				status = 'E'
			else:
				status = ' '
			
			# print('GE %s - %s - %s' % (ge.identifier, status, uptake))
			out.write('| %s    |  %s  | %s       |' % (ge.identifier, status, uptake))
		# out.write('| ...   | ...   | ...      |')
	
	
	
	