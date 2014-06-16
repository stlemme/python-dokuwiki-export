
from presenter import PresenterBase
from visitor import GEVisitor, UsedByVisitor


class GESurveyPresenter(PresenterBase):
	def __init__(self, hideunused = False):
		PresenterBase.__init__(self)
		self.v = GEVisitor()

	def present(self, meta):
		self.v.visit(meta)
		self.validation = {}
		
		for ge in self.v.result:
			uv = UsedByVisitor(ge, ['USES', 'WILL USE', 'MAY USE'], se=True, app=True, experiment=False, transitive=False)
			uv.visit(meta)
			
			uve = set(uv.result)
			
			ses = [e for e in uve if e.entity == 'SE']
			apps = [e for e in uve if e.entity == 'APP']

			
			for se in ses:
				partner, contact = se.provider
				
				if not partner in self.validation:
					self.validation[partner] = {"contacts" : set(), "GEs" : set()}
					
				self.validation[partner]["contacts"].add(contact)
				self.validation[partner]["GEs"].add(ge)

			for app in apps:
				partner, contact = app.developer
				
				if not partner in self.validation:
					self.validation[partner] = {"contacts" : set(), "GEs" : set()}
					
				self.validation[partner]["contacts"].add(contact)
				self.validation[partner]["GEs"].add(ge)

				
	def dump(self, out):
		out.write('^ Partner  ^ Contacts  ^ GEs  ^')
		partners = list(self.validation.keys())
		partners.sort(key = lambda p: p.identifier)
		for partner in partners:
			val = self.validation[partner]
			contacts = list(val["contacts"])
			contacts.sort(key = lambda p: p)
			ges = [ge.identifier for ge in val["GEs"]]
			ges.sort(key = lambda p: p)
			out.write('| %s    |  %s  | %s       |' % (partner.identifier, " \\\\ ".join(contacts), " \\\\ ".join(ges)))
		# out.write('| ...   | ...   | ...      |')
