
import logging
from . import ProcessingGenerator


class TemplatedGenerator(ProcessingGenerator):

	def __init__(self, template, escaping = lambda t : t):
		ProcessingGenerator.__init__(self, escaping)
		self.template = template
	
	def generate_entry(self, se):
		self.se = se
		
		entry = self.template[:]
		
		# print(self.se.get('/auto'))
		# print(self.se.get('/spec'))

		entry = self.process_text_snippet(entry)
		self.se = None
		
		return entry
