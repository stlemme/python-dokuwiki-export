
class PresenterBase(object):
	def __init__(self):
		self.fixmes = []
		
	def present(self, meta):
		pass

	def dump(self, out):
		pass

	def dump_fixmes(self, out):
		for f in self.fixmes:
			out.write(f)
			out.write('')
	
	def fixme(self, addressee, todo, deadline = None):
		if isinstance(addressee, list):
			addressee = ', '.join(list(set(addressee)))
		if deadline is not None:
			deadline = '{' + deadline + '}'
		else:
			deadline = ''
		fixme = "FIXME [{0}] {1} {2}".format(addressee, deadline, todo)
		self.fixmes.append(fixme)
