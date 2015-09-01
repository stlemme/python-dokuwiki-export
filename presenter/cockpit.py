
from . import PresenterBase
# import releases
# from entities import InvalidEntity


products = {
	"Recommendation Services": "REPERIO",
	"Virtual/Mixed Reality": "KIWANO",
	"Content Similarity": "Search & Discovery"
}


class CockpitPresenter(PresenterBase):
	
	def __init__(self, columns, nice = lambda item: item, sort = [], placeholder = "n/a"):
		PresenterBase.__init__(self)
		self.available_columns = {
			"name":             ("Specific Enabler", self.lookup_name),
			"avail-fi-ppp":     ("availability for the FI-PPP partners", None),
			"avail-fi-lab":     ("availability within FI-LAB", None),
			"avail-3rd-party":	("availability beyond the FI-PPP", None),
			"product":			("SE implementation product(s) name(s)", self.lookup_product),
			"owner":			("Owner", self.lookup_owners),
			"open-source":		("Open Source (Yes/No/Planned)", self.lookup_opensource),
			"mode":				("mode", self.lookup_mode),
			"last-update":		("date last update", None),
			"next-update":		("date next / 1st update", None),
			"assets":			("Baseline assets", self.lookup_assets),
			"catalog":			("Entry in Catalogue", self.lookup_catalog),
			"final-release":	("Final release", lambda se: self.lookup_release('08/15', se)),
			"roadmap":			("Roadmap", self.lookup_roadmap)
		}

		self.columns = [col for col in columns if col in self.available_columns]
		self.nice = nice
		self.placeholder = placeholder
		self.sort = [self.columns.index(col) for col in sort if col in self.columns]

	def lookup_release(self, rel, se):
		return 'X' if self.final_release.contains_se(se) else ''
		
	def lookup_product(self, se):
		id = se.get_name()
		if id in products:
			return products[id]
		return '-'
		
	def lookup_roadmap(self, se):
		nc = se.get_naming_conventions()
		if nc is None:
			return self.placeholder
		roadmap = nc.roadmap()
		if roadmap is None:
			return self.placeholder
		return roadmap
		
	# def lookup_availability(self, se):
		# return self.currentrelease.contains_se(se)
	def lookup_name(self, se):
		name = self.nice(se)
		if name is None:
			return self.placeholder
		return name
		
	def lookup_owners(self, se):
		owners = se.get('/spec/owners')
		if owners is None:
			return '[[UNKNOWN OWNER]]'
		return ', '.join(owners)
	
	def lookup_status(self, se):
		if self.final_release.contains_se(se):
			return 'available'
		status = se.get('/status')
		if status is None:
			return self.placeholder
		return status
	
	def lookup_assets(self, se):
		wiki = se.get('/auto/documentation/wiki-url')
		if wiki is None:
			return self.placeholder
		return wiki
	
	def lookup_catalog(self, se):
		# if not self.lookup_availability(se):
			# return 'not (yet) available'
		nc = se.get_naming_conventions()
		if nc is None:
			return self.placeholder
		return nc.catalogurl()
	
	def lookup_opensource(self, se):
		open = se.get('/auto/license/is-open-source')
		if open is None:
			return self.placeholder
		return open
		
	def lookup_mode(self, se):
		mode = []
		
		if se.get('/auto/license/is-open-source') == 'Yes':
			template = se.get('/spec/license/template')
			mode.append('open source (%s)' % template)
			
		if se.get('/auto/delivery/hosted-service') == 'Yes':
			saas = 'SaaS'
			if se.get('/spec/delivery/instances/public') is not None:
				saas = 'Global SaaS instance'
			elif se.get('/spec/delivery/instances/fi-ppp') is not None:
				saas = 'Dedicated SaaS instance'
			mode.append(saas)

		binary = se.get('/spec/delivery/binary')
		if binary is not None:
			platforms = ', '.join(binary.keys())
			mode.append('binaries (%s)' % platforms)
			
		if len(mode) == 0:
			return self.placeholder
		
		return ', '.join(mode)

	def present_col(self, se, colname):
		if colname not in self.available_columns:
			return self.placeholder
		col = self.available_columns[colname]
		f = col[1]
		if f is None:
			return self.placeholder
		v = f(se)
		if v is None:
			return self.placeholder
		return v
		
	def present_se(self, se):
		return [self.present_col(se, colname) for colname in self.columns]
	
	def present(self, meta):
		# self.currentrelease = meta.find_current_release()
		rels = meta.get_releases()
		self.final_release = rels[-1]
		self.rows = [self.present_se(se) for se in meta.get_specific_enablers()]
		
		if len(self.sort) > 0:
			self.rows.sort(key = lambda row: tuple([row[idx] for idx in self.sort]))

	def dump_row(self, out, row, sep = '|'):
			out.write((sep + ' %s ' + sep) % ((' ' + sep + ' ').join(row)))

	def dump(self, out):
		headings = [self.available_columns[colname][0] for colname in self.columns]
		self.dump_row(out, headings, '^')
		
		for row in self.rows:
			self.dump_row(out, row)

