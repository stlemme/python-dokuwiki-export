
from . import PresenterBase
from visitor import UsedByVisitor
from entities import SpecificEnabler, DeprecatedSpecificEnabler, Application


class ResourcesPresenter(PresenterBase):
	def __init__(self, dw, se, nice = lambda item: item):
		PresenterBase.__init__(self)
		self.dw = dw
		self.se = se
		self.nice = nice
		self.resources = []

	def push(self, link, caption):
		t = (link, caption)
		self.resources.append(t)
		
	def add_path(self, path, caption):
		val = self.se.get(path)
		if val is None:
			return
		self.push(val, caption)
	
	def present(self, meta):
		self.resources = []
		nc = self.se.get_naming_conventions()
		
		self.add_path('/auto/documentation/wiki-url', 'Technical documentation of %s')
		self.add_path('/auto/documentation/devguide-url', 'Developer guide of %s')
		self.add_path('/auto/documentation/installguide-url', 'Installation guide of %s')
		# self.add_path('/auto/documentation/api-url', 'API Description of %s')
		self.add_path('/auto/usage/online-demo/link', 'Demo application of %s')
		

	def dump(self, out):
		if len(self.resources) == 0:
			out.write('n/a')
			return
		
		for item in self.resources:
			url = item[0]
			line = item[1] % self.nice(self.se)
			out.write('  * %s' % self.dw.link(url, None, line))
