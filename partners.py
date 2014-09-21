
from jsonutils import Values
import logging


class Partners(Values):
	def __init__(self, partner_contacts):
		Values.__init__(self, partner_contacts)
		
		
	def get_person(self, name):
		parts = name.split('-', 2)
		partnername = parts[0]
		personname = parts[1]

		company = self.get('/' + partnername + '/company')
		person = self.get('/' + partnername + '/members/' + personname)
		if person is None:
			logging.warning("Unknown person %s of partner %s" % (personname, partnername))
			return None
		
		person = dict(person)
		person['company'] = company
		return person
	