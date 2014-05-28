
from presenter import PresenterBase
import re
from visitor import ExperimentsVisitor, DependencyVisitor


class DependencyPresenter(PresenterBase):
	def __init__(self, scenario, site = None, relations = ['USES']):
		PresenterBase.__init__(self)
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
		sedge = edge.replace(' ', '_')
		self.dump_line('%s:%s -> %s [style = %s, color = "%s", fontsize = %s, fontcolor = "%s", label = "%s"];' % (
				id1,
				self.lookup_design('tailport', ['EDGE_%s' % sedge, 'EDGE']),
				id2,
				self.lookup_design('style', ['EDGE_%s' % sedge, 'EDGE']),
				self.lookup_design('color', ['EDGE_%s' % sedge, 'EDGE']),
				self.lookup_design('fontsize', ['EDGE_%s' % sedge, 'EDGE']),
				self.lookup_design('color', ['EDGE_%s' % sedge, 'EDGE']),
				self.lookup_timing(node1, node2, edge)
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

	def lookup_timing(self, node1, node2, edge):
		if edge == 'USES':
			return "    "
		
		if node2 not in node1.timing:
			logging.fatal("Missing timing information!")

		timing = node1.timing[node2]

		if timing is None:
			if node1.entity == 'SE':
				responsible = node1.provider
			elif node1.entity == 'APP':
				responsible = node1.developer
			else:
				logging.fatal("Unknown entity (neither APP nor SE)")
			
			self.fixme(
				responsible[0].identifier,
				'Provide a timeframe for the integration of enabler "%s" in enabler/application "%s"' % (node2.identifier, node1.identifier),
				deadline = 'ASAP'
			)
			return "No timeframe"
			
		return timing[0]
	
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
			self.fixme(
				[exp.conductor[0].identifier for exp in self.ev.result],
				'Provide deployment information for enabler "%s" in scenario "%s" on site %s' % (enabler.identifier, self.scenario, self.site),
				deadline = 'ASAP'
			)
			return "no deployment info"
		return ', '.join([l.identifier for l in set(locs)])
	
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
		
		self.dump_fixmes(out)
		
		self.out = None
