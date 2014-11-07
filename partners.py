
from jsonutils import Values
import logging


class Partners(Values):
	def __init__(self, partner_contacts):
		Values.__init__(self, partner_contacts)
		
		
	def get_person(self, name):
		parts = name.split('-', 2)
		partnername = parts[0]

		company = self.get('/' + partnername + '/company')
		if company is None:
			logging.warning("Unknown partner %s" % partnername)
			return None
		
		if len(parts) > 1:
			personname = parts[1]
		else:
			personname = company.get('primary')
			if personname is None:
				logging.warning("No primary contact for partner %s" % partnername)
				return None
		
		person = self.get('/' + partnername + '/members/' + personname)
		if person is None:
			logging.warning("Unknown person %s of partner %s" % (personname, partnername))
			return None
		
		# person = dict(person)
		person.set('company', company)
		return person
	