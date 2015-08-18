
from . import PresenterBase
from visitor import UsedByVisitor
from entities import SpecificEnabler, DeprecatedSpecificEnabler, Application


class ReleaseCyclePresenter(PresenterBase):
	def __init__(self, dw, se, nice = lambda item: item):
		PresenterBase.__init__(self)
		self.dw = dw
		self.se = se
		self.nice = nice
		self.flags = []
		self.space = ' '*2

	def push(self, rel, flag):
		t = (rel, flag)
		self.flags.append(t)
		
	def present(self, meta):
		for rel in meta.get_releases():
			f = 'X' if rel.contains_se(self.se) else ' '
			self.push(rel.get_name(), f)

	def dump(self, out):
		beg = '|' + self.space
		sep = self.space + '|' + self.space
		end = self.space + '|'
		linet = sep.join([f[0] for f in self.flags])
		lineb = sep.join([f[1] for f in self.flags])
		out.write(beg + linet + end)
		out.write(beg + lineb + end)
