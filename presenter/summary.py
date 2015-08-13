
from . import PresenterBase
# import releases
# from entities import InvalidEntity




class SummaryPresenter(PresenterBase):
	def __init__(self, placeholder = "n/a", mark = 'X'):
		PresenterBase.__init__(self)
		self.placeholder = placeholder
		self.mark = mark
		self.unmark = ''

	def print_mark(self, mark):
		return self.mark if mark else self.unmark
	
	
	def lookup_meta(self, se):
		if se.get_metapage() is None:
			return False
		if se.get('/metajson') is None:
			return False
		return se.get('/spec') is not None

		
	def lookup_availability(self, se):
		rel = self.meta.find_current_release()
		if rel is None:
			return False
		return rel.contains_se(se)
		
	def lookup_devguide(self, se):
		return se.get('/auto/documentation/devguide-url') is not None
	
	def lookup_catalog(self, se):
		return self.lookup_availability(se)
	
	def lookup_video(self, se):
		return se.get('/auto/media/youtube-pitch') is not None

	def lookup_examples(self, se):
		examples = se.get('/spec/examples')
		if examples is None:
			return '0'
		return str(len(examples))

	def lookup_github(self, se):
		return se.get('/spec/delivery/repository/github') is not None

	def present_se(self, se):
		return (
			se.get_name(),           # name
			self.print_mark(self.lookup_meta(se)),     # meta
			self.print_mark(self.lookup_devguide(se)), # devguide in wiki
			self.print_mark(self.lookup_video(se)),    # video pitch
			self.lookup_examples(se),                  # number of examples
			self.print_mark(self.lookup_github(se)),   # already available on github
			self.print_mark(self.lookup_catalog(se))   # catalog entry available
		)
	
	def present(self, meta):
		self.summary = []
		self.meta = meta
		
		for se in meta.get_specific_enablers():
			row = self.present_se(se)
			self.summary.append(row)

		self.summary.sort(key = lambda tup: (tup[0]))
		
	def dump(self, out):
		heading = [
			"SE",
			"Meta",
			"Developer Guide",
			"Video Pitch",
			"Examples",
			"github",
			"Catalogue"
		]
		
		out.write('^ %s ^' % (' ^ '.join(heading)))
		
		for se in self.summary:
			out.write('| %s | %s | %s | %s | %s | %s | %s |' % se)
			# out.write('| %s | %s / %s | | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % exp)

		for ise in self.meta.get_invalid_specific_enablers():
			out.write(('| %s |' % ise.get_name()) + (' %s |' % self.placeholder) * (len(heading) - 1))
