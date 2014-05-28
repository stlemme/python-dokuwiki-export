
from presenter import PresenterBase
from visitor import GEVisitor, UsedByVisitor


class UptakePresenter(PresenterBase):
	def __init__(self, hideunused = False):
		PresenterBase.__init__(self)
		self.v = GEVisitor()
		self.hideunused = hideunused

	def present(self, meta):
		self.v.visit(meta)
		self.uptake = []
		
		for ge in self.v.result:
			uv1 = UsedByVisitor(ge, ['USES'], se=True, app=True, experiment=False)
			uv1.visit(meta)
			uv2 = UsedByVisitor(ge, ['USES', 'WILL USE'], se=True, app=True, experiment=False)
			uv2.visit(meta)
			# uv2b = UsedByVisitor(ge, 'USES', se=True, app=True, experiment=False, transitive=['USES', 'WILL USE'])
			# uv2b.visit(meta)
			uv3 = UsedByVisitor(ge, ['USES', 'WILL USE', 'MAY USE'], se=True, app=True, experiment=False)
			uv3.visit(meta)
			# uv3b = UsedByVisitor(ge, 'WILL USE', se=True, app=True, experiment=False, transitive=['USES', 'WILL USE', 'MAY USE'])
			# uv3b.visit(meta)
			# uv3c = UsedByVisitor(ge, 'USES', se=True, app=True, experiment=False, transitive=['USES', 'WILL USE', 'MAY USE'])
			# uv3c.visit(meta)

			if self.hideunused and len(uv1.result)+len(uv2.result)+len(uv3.result) == 0:
				continue
				
			uv1e = set(uv1.result)
			uv2e = set(uv2.result) - (uv1e       )
			uv3e = set(uv3.result) - (uv1e | uv2e)
			
			# def printid(eset):
				# return [e.identifier for e in list(eset)]

			# def printe(eset):
				# return [e.usestates for e in list(eset)]
				
			# if ge.identifier == "POI Data Provider":
				# print(ge.identifier)
				# print(uv1.result)
				# print(printe(uv1.result))
				# print(uv2.result)
				# print(printid(uv2b.result))
				# print(uv3.result)
				# print(printid(uv3b.result))
				# print(printid(uv3c.result))
				# print()
			# else:
				# print(ge.identifier)
				# print(printid(uv1.result))
				# print(printid(uv2.result))
				# print(printid(uv2b.result))
				# print(printid(uv3.result))
				# print(printid(uv3b.result))
				# print(printid(uv3c.result))
				# print()
			
			self.uptake.append((ge, list(uv1e), list(uv2e), list(uv3e)))

		# self.experiments.sort(key = lambda tup: (parsedate(tup[0]), tup[2]))
		
	def dump(self, out):
		out.write('^ GE  ^  Uptake  ^ SEs / Applications  ^')
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
