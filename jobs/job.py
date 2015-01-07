

class Job(object):
	def __init__(self):
		pass
		
	def summary(self):
		return "Unknown Job"

	def required(self):
		return False
		
	def perform(self, fidoc):
		return False
		
	def responsible(self, fidoc):
		return None
		
