


class wikipublisher(object):
	def __init__(self, dw, publish_ns, exceptions = [], export_ns = []):
		self.dw = dw
		self.publish_ns = publish_ns
		self.exceptions = exceptions
		self.export_ns = export_ns
		
		
	def public_page(self, page, rel_ns = []):
		fullname = self.dw.resolve(page, rel_ns)
		
		result = self.publish_ns.match(fullname)
		if result is None:
			return None
			
		for rx in self.exceptions:
			if rx.match(fullname) is not None:
				return None
				
		fullname = fullname.replace(':', '.').strip('.')
		
		if fullname.endswith(".start"):
			fullname = fullname[:-6]
			
		fullname = self.dw.resolve(fullname, self.export_ns)
		return fullname
		
