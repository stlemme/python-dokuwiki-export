
from . import PresenterBase
from visitor import UsedByVisitor
from metastructure import SpecificEnabler, Application


class UptakePresenter(PresenterBase):
	def __init__(self, hideunused = False):
		PresenterBase.__init__(self)
		# self.v = GEVisitor()
		self.hideunused = hideunused
		self.collect_entities = [SpecificEnabler, Application]

	def present_ge(self, ge, meta):
		uv1 = UsedByVisitor(ge, ['USES'], self.collect_entities)
		uv1.visit(meta)
		uv2 = UsedByVisitor(ge, ['USES', 'WILL USE'], self.collect_entities)
		uv2.visit(meta)
		uv3 = UsedByVisitor(ge, ['USES', 'WILL USE', 'MAY USE'], self.collect_entities)
		uv3.visit(meta)
		
		uv1e = set(uv1.get_result())
		uv2e = set(uv2.get_result()) - (uv1e       )
		uv3e = set(uv3.get_result()) - (uv1e | uv2e)
		
		return (ge, list(uv1e), list(uv2e), list(uv3e))
		
	
	def present(self, meta):
		self.uptake = []
		
		for ge in meta.get_generic_enablers():
			row = self.present_ge(ge, meta)
			if self.hideunused and len(row[1])+len(row[2])+len(row[3]) == 0:
				continue
			self.uptake.append(row)


	def dump(self, out):
		out.write('^ GE  ^  Uptake  ^ SEs / Applications  ^')
		for ge, uses, will, may in self.uptake:
			ses = ['%s SE' % e.get_name() for e in uses if isinstance(e, SpecificEnabler)]
			apps = ['%s' % e.get_name() for e in uses if isinstance(e, Application)]

			wses = ['//%s SE//' % e.get_name() for e in will + may if isinstance(e, SpecificEnabler)]
			wapps = ['//%s//' % e.get_name() for e in will + may if isinstance(e, Application)]

			se_uptake = ' \\\\ '.join(ses + wses)
			app_uptake = ' \\\\ '.join(apps + wapps)
			
			if len(se_uptake) == 0:
				se_uptake = ':::'
			
			if len(uses):
				status = 'D'
			elif len(will):
				status = 'U'
			elif len(may):
				status = 'E'
			else:
				status = ' '
			
			# print('GE %s - %s - %s' % (ge.identifier, status, uptake))
			out.write('| %s    |  %s  | %s       |' % (ge.get_name(), status, app_uptake))
			out.write('| :::   |  ::: | %s       |' % se_uptake)
		# out.write('| ...   | ...   | ...      |')
