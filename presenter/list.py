
from . import PresenterBase


class ListPresenter(PresenterBase):
	def __init__(self, visitor, nice = lambda item: item):
		PresenterBase.__init__(self)
		self.v = visitor
		self.nice = nice
		
	def present(self, meta):
		self.v.visit(meta)
		self.list = self.v.result
		# print(self.v.result)
		# print(self.v.nodes)
		
	def dump(self, out):
		for item in self.list:
			out.write('  * %s' % self.nice(item))

