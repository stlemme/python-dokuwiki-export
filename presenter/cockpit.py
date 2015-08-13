
from . import PresenterBase
# import releases
# from entities import InvalidEntity


products = {
	"Recommendation Services": "REPERIO",
	"Virtual/mixed Reality": "KIWANO",
	"Content Similarity": "Search & Discovery"
}


class CockpitPresenter(PresenterBase):
	def __init__(self, placeholder = "n/a"):
		PresenterBase.__init__(self)
		self.placeholder = placeholder

	def lookup_product(self, se):
		id = se.get_name()
		if id in products:
			return products[id]
		return '-'
		
	def lookup_roadmap(self, se):
		nc = se.get_naming_conventions()
		if nc is None:
			return None
		roadmap = nc.roadmap()
		return roadmap
		
	# def lookup_availability(self, se):
		# return self.currentrelease.contains_se(se)
		
	def lookup_owners(self, se):
		owners = se.get('/spec/owners')
		if owners is None:
			return '[[UNKNOWN OWNER]]'
		return ', '.join(owners)
	
	def lookup_status(self, se):
		if self.currentrelease.contains_se(se):
			return 'available'
		status = se.get('/status')
		if status is None:
			return self.placeholder
		return status
	
	def lookup_wikipage(self, se):
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

	def present_se(self, se):
		# if isinstance(se, InvalidEntity):
			# return (
				# se.get_name(),    # name
				# self.placeholder, # product
				# self.placeholder, # owner
				# self.placeholder, # Open Source?
				# self.placeholder, # FI-PPP mode
				# '', # FI-PPP date
				# '', # FI-PPP date
				# self.placeholder, # FI-LAB mode
				# '', # FI-LAB date
				# '', # FI-LAB date
				# self.placeholder, # others mode
				# '', # others date
				# self.placeholder, # wiki page
				# self.placeholder  # catalog entry
			# )
	
		return (
			se.get_name(),           # name
			self.lookup_product(se), # product
			self.lookup_owners(se),  # owner
			self.lookup_opensource(se), # Open Source?
			self.lookup_mode(se), # FI-PPP mode
			'', # FI-PPP date
			'', # FI-PPP date
			# self.lookup_mode(se), # FI-LAB mode
			# '', # FI-LAB date
			# '', # FI-LAB date
			# self.lookup_mode(se), # others mode
			# '', # others date
			self.lookup_wikipage(se), # wiki page
			self.lookup_catalog(se) # catalog entry
		)
	
	def present(self, meta):
		self.currentrelease = meta.find_current_release()
		self.exploitation = []
		
		for se in meta.get_specific_enablers():
			row = self.present_se(se)
			self.exploitation.append(row)

		self.exploitation.sort(key = lambda tup: (tup[7], tup[0]))
		
	def dump(self, out):
		heading = [
			"availability for the FI-PPP partners",
			"availability within FI-LAB",
			"availability beyond the FI-PPP",
			"FI-PPP SEs",
			"SE implementation product(s) name(s) / owner",
			# "",
			"Open Source (Yes/No/Planned)",
			"mode",
			"date last update",
			"date next / 1st update",
			# "mode",
			# "date last update",
			# "date next / 1st update",
			# "currently planned mode",
			# "when",
			"Baseline assets",
			"Entry in Catalogue"
		]
		
		out.write('^ ^^^ %s ^^^ ^^' % "availability")
		# out.write('^ ^^^^ %s ^^^ %s ^^^ %s ^^ ^^' % tuple(heading[0:3]))
		out.write('^ %s ^' % (' ^ '.join(heading[3:])))
		
		for exp in self.exploitation:
			out.write('| %s | %s / %s | %s | %s | %s | %s | %s | %s |' % exp)
			# out.write('| %s | %s / %s | | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % exp)

