
import metagenerate
import logging



class Notifier(object):
	def notify(person, subject, content):
		pass

	
class EmailNotifier(Notifier):
	fromaddress = "dokuwikibot@wiki.mediafi.org"
	ccaddress = ["stefan.lemme@dfki.de", "dirkk0@googlemail.com"]
	
	def __init__(self):
		self.send = None
		
		try:
			import sendmail
			self.send = lambda s, fr, to, cc, sub, msg: sendmail.send(fr, to, cc, sub, msg)
		except ImportError as e:
			logging.error("Unable to import sendmail support.")
		
	def email(self, contactname):
		return None

	def notify(self, person, subject, message):
		address = self.email(person)
		print("Send mail to %s" % address)
		if address is None:
			return False
		
		if self.send is None:
			return False
		
		return self.send(
			self.fromaddress,
			["stefan.lemme@dfki.de"],
			self.ccaddress,
			subject,
			message
		)

	
			
class MetaNotifier(EmailNotifier):
	def __init__(self, dw, metapage):
		EmailNotifier.__init__(self)
		
		self.dw = dw
		metadoc = dw.getpage(metapage)
		if metadoc is None:
			logging.error("Meta structure %s not found." % metapage)

		meta, self.data = metagenerate.process_meta(metadoc)
		if meta is None:
			logging.error("Invalid meta structure %s." % metapage)
			
		if len(self.data.partner) == 0:
			logging.error("No contact information available.")


	def email(self, contactname):
		# print(self.data.partner)
		p, c = self.data.contact(contactname)
		if p is None:
			return None
		return p.contacts[c]


import re

class UserFileNotifier(EmailNotifier):
	def __init__(self, userfile):
		EmailNotifier.__init__(self)
		self.mails = {}
		
		if userfile is None:
			return
				
		with open(userfile) as users:
			for line in users:
				if line.strip().startswith('#'):
					continue
				
				result = line.split(':')
				if len(result) != 5:
					continue
				
				self.mails[result[0]] = result[3]

	def email(self, contactname):
		# print(self.mails)
		if contactname in self.mails:
			return self.mails[contactname]
		return None
