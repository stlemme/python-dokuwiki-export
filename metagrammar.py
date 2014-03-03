
from modgrammar import *


grammar_whitespace_mode = 'explicit'


class MetaError(Exception):
	def __init__(self, problem, text):
		self.problem = problem
		self.text = text
		
	def __str__(self):
		return "%s\nused in:\n%s" % (self.problem, self.text)
	
class UnknownEnabler(MetaError):
	def __init__(self, enabler, text):
		MetaError.__init__(self, 'Unknown Enabler (SE/GE) "%s"' % enabler, text)
		
class UnknownApplication(MetaError):
	def __init__(self, app, text):
		MetaError.__init__(self, 'Unknown application: "%s"' % app, text)

class UnknownLocation(MetaError):
	def __init__(self, loc, text):
		MetaError.__init__(self, 'Unknown deployment location: "%s"' % loc, text)

class UnknownPartner(MetaError):
	def __init__(self, partner, text):
		MetaError.__init__(self, 'Unknown partner: "%s"' % partner, text)

class InvalidTimeframe(MetaError):
	def __init__(self, problem, text):
		MetaError.__init__(self, 'Invalid timeframe: "%s"' % problem, text)

		
###############

class Identifier(Grammar):
	grammar = (WORD("[\w,\-!\&\(\)\/]", "[\w ,\-!\&\(\)\/]*", fullmatch=False, escapes=True, greedy=False))

class RedIdentifier(Grammar):
	grammar = (WORD("[\w]", "[\w \-!\(\)\/]*", fullmatch=False, escapes=True, greedy=False))
	
class AsStatement(Grammar):
	grammar = (LITERAL("AS"), WHITESPACE, LIST_OF(RedIdentifier, sep=",", whitespace_mode='optional'))
	# grammar_whitespace_mode = 'required'
	# grammar_collapse = True

class NamedEntity(Grammar):
	# grammar = (LITERAL(    ), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AsStatement))
	# grammar_whitespace_mode = 'required'
	
	def grammar_elem_init(self, data):
		self.identifier = self.elements[2].string
		self.aliases = []
		self.entity = self.__class__.__name__

		if self.elements[3] is not None:
			self.aliases = [alias.string for alias in self.elements[3].find_all(RedIdentifier)]

	def register_name(self, map, data):
		if self.identifier in map.keys():
			data.warning("%s %s already declared! Previous will be overwritten." % (self.entity, self.identifier))
			
		map[self.identifier] = self
		
		for a in self.aliases:
			e = data.enabler(a)
			if e is not None:
				data.warning('Alias name "%s" for %s %s is already in use for %s %s. Redefinition ignored!' % (a, self.entity, self.identifier, e.entity, e.identifier))
				continue
			map[a] = self


###############

class GE(NamedEntity):
	grammar = (LITERAL("GE"), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AsStatement))
	# grammar_whitespace_mode = 'required'
	
	def grammar_elem_init(self, data):
		NamedEntity.grammar_elem_init(self, data)
		self.register_name(data.ge, data)

	
###############

# TODO: restrict to any type of date (M12, Release 06/14, February 2014)
class PointInTime(Grammar):
	grammar = (WORD("[\w]", "[\w \(\)\/]*", fullmatch=False, escapes=True, greedy=False))
	
class TimeframeStmt(Grammar):
	grammar = (WHITESPACE, LITERAL("FROM"), WHITESPACE, PointInTime, WHITESPACE, LITERAL("ON"))
	
import date

def validateTimeframe(pit):
	# TODO: validate against various regexp, fuzzy date parsing, etc.
	# TODO: store respective datetime object
	tf = date.parseProjectDate(pit)
	if tf < date.projectbegin or tf > date.projectend:
		logging.warning("Timeframe outside of project course: %s (%s)" % (pit, tf))
	return (pit, tf)

class UseStmt(Grammar):
	grammar = (
		OR(
			LITERAL("USES"),
			LITERAL("WILL USE"),
			LITERAL("MAY USE")
		),
		OPTIONAL(TimeframeStmt),
		WHITESPACE,
		LIST_OF(RedIdentifier, sep=",", whitespace_mode='optional')
	)
	
def handleUseStmts(stmts, usestates, timing, data, hint):
	for u in stmts.find_all(UseStmt):
		usestate = u.elements[0].string
		# print(u.elements[0].elements)

		timeframe = None
		if u.elements[1] is not None:
			if usestate == "USES":
				raise InvalidTimeframe("Timeframe for USES relation neither allowed nor necessary!")
			
			timeframe = validateTimeframe(u.elements[1].elements[3].string)
			# TODO: check return value
		# print(timeframe)
			
		enablers = [e.string for e in u.elements[3].find_all(RedIdentifier)]
		# print(enablers)
		# l = [e for e in [data.enabler(e) for e in enablers] if e is not None]
		for ename in enablers:
			e = data.enabler(ename)
			if e is None:
				raise UnknownEnabler(ename, hint)
			usestates[usestate].append(e)
			timing[e] = timeframe
			# print('Enabler %s integrated by %s' % (e.identifier, timeframe))

def handleContact(elem, data, hint):
	if elem is None:
		return None
	
	partnername = elem.elements[5].string
	partner, contact = data.contact(partnername)
	if partner is None:
		raise UnknownPartner(partnername, hint)
	return (partner, contact)
	# print(self.provider)


class SE(NamedEntity):
	grammar = (
		LITERAL("SE"), WHITESPACE, Identifier,
		OPTIONAL(WHITESPACE, AsStatement),
		OPTIONAL(WHITESPACE, LITERAL("PROVIDED"), WHITESPACE, LITERAL("BY"), WHITESPACE, RedIdentifier),
		ZERO_OR_MORE(WHITESPACE, UseStmt)
	)

	def grammar_elem_init(self, data):
		NamedEntity.grammar_elem_init(self, data)
		self.register_name(data.se, data)
		
		# extract uses, will use, and may use statements
		self.uses = []
		self.willuse = []
		self.mayuse = []
		
		self.usestates = {
			"USES": self.uses,
			"WILL USE": self.willuse,
			"MAY USE": self.mayuse
		}
		
		self.timing = {}
		
		self.provider = handleContact(self.elements[4], data, self.string)
		
		if self.elements[5] is not None:
			handleUseStmts(self.elements[5], self.usestates, self.timing, data, self.string)


###############

class LOC(NamedEntity):
	grammar = (LITERAL("LOC"), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AsStatement))
	# grammar_whitespace_mode = 'required'
	
	def grammar_elem_init(self, data):
		NamedEntity.grammar_elem_init(self, data)
		self.register_name(data.loc, data)

###############

class APP(NamedEntity):
	grammar = (
		LITERAL("APP"), WHITESPACE, Identifier,
		OPTIONAL(WHITESPACE, AsStatement),
		OPTIONAL(WHITESPACE, LITERAL("DEVELOPED"), WHITESPACE, LITERAL("BY"), WHITESPACE, RedIdentifier),
		ONE_OR_MORE(WHITESPACE, UseStmt)
	)

	def grammar_elem_init(self, data):
		NamedEntity.grammar_elem_init(self, data)
		self.register_name(data.app, data)
		
		# extract uses, will use, and may use statements
		self.uses = []
		self.willuse = []
		self.mayuse = []
		
		self.usestates = {
			"USES": self.uses,
			"WILL USE": self.willuse,
			"MAY USE": self.mayuse
		}
		
		self.timing = {}
		
		self.developer = handleContact(self.elements[4], data, self.string)

		if self.elements[5] is not None:
			handleUseStmts(self.elements[5], self.usestates, self.timing, data, self.string)


###############

class Place(Grammar):
	grammar = (Identifier)

class Date(Grammar):
	grammar = (Identifier)

class ExperimentationSite(Grammar):
	grammar = (Identifier)

class Scenario(Grammar):
	grammar = (Identifier)

class DeploymentStmt(Grammar):
	grammar = (LITERAL("WITH"), WHITESPACE, LIST_OF(RedIdentifier, WHITESPACE, LITERAL("DEPLOYED"), WHITESPACE, LITERAL("AT"), WHITESPACE, RedIdentifier, sep=',', whitespace_mode='optional'))


class EXPERIMENT(Grammar):
	grammar = (
		LITERAL("EXPERIMENT"), WHITESPACE, LITERAL("IN"), WHITESPACE, Place,
		OPTIONAL(WHITESPACE, LITERAL("OF"), WHITESPACE, LITERAL("SITE"), WHITESPACE, ExperimentationSite),
		WHITESPACE, LITERAL("AT"), WHITESPACE, Date,
		OPTIONAL(WHITESPACE, LITERAL("CONDUCTED"), WHITESPACE, LITERAL("BY"), WHITESPACE, RedIdentifier),
		WHITESPACE, LITERAL("DRIVES"), WHITESPACE, Scenario,
		ONE_OR_MORE(WHITESPACE, DeploymentStmt),
		WHITESPACE, LITERAL("BY"), WHITESPACE, LITERAL("RUNNING"), WHITESPACE, Identifier
	)

	def grammar_elem_init(self, data):
		self.place = self.elements[4].string
		self.site = self.place
		if self.elements[5] is not None:
			self.site = self.elements[5].elements[5].string
			
		self.date = self.elements[9].string
		self.scenario = self.elements[14].string
		
		self.conductor = handleContact(self.elements[10], data, self.string)
		
		self.application = data.application(self.elements[21].string)
		if self.application is None:
			raise UnknownApplication(self.elements[21].string, self.string)
		
		self.deployment = {}
		for d in self.elements[15].find_all(DeploymentStmt):
			for ed in d.elements[2]:
				if not len(ed.elements):
					continue
				ename = ed.elements[0].string
				locname = ed.elements[6].string
				# print("%s  --  %s" % (ename, locname))
				e = data.enabler(ename)
				l = data.location(locname)
				if e is None:
					raise UnknownEnabler(ename, self.string)
				if l is None:
					raise UnknownLocation(locname, self.string)
				# TODO: check if it's overwritten
				self.deployment[e] = l
				
		# TODO: check for complete deployment information

###############

class MailAddress(Grammar):
	grammar = (WORD("\w", "[\w\.\-@\+]", fullmatch=False, escapes=True, greedy=False))

class PARTNER(Grammar):
	grammar = (
		LITERAL("PARTNER"), WHITESPACE, RedIdentifier,
		ONE_OR_MORE(
			WHITESPACE, LITERAL("WITH"), WHITESPACE, Identifier,
			WHITESPACE, LITERAL("-"), WHITESPACE,
				MailAddress,
				OPTIONAL(
					WHITESPACE, LITERAL("AS"), WHITESPACE, LITERAL("DEFAULT"), WHITESPACE, LITERAL("CONTACT")
					# whitespace_mode='required'
				)
		)
	)
	
	def grammar_elem_init(self, data):
		self.identifier = self.elements[2].string
		self.contacts = {}
		self.defaultcontact = None
		for elem in self.elements[3].elements:
			name = elem.elements[3].string
			email = elem.elements[7].string
			self.contacts[name] = email
			if elem.elements[8] is not None:
				self.defaultcontact = name
				
		if self.defaultcontact is None:
			self.defaultcontact = self.elements[3].elements[0].elements[3].string

		# print(self.identifier)
		# print(self.contacts)
		# print(self.defaultcontact)
		
		data.partner[self.identifier] = self


###############

class Meta(Grammar):
	grammar = (BOL, OR(GE, SE, LOC, APP, EXPERIMENT, PARTNER, WHITESPACE, EMPTY), EOL)

class MyGrammar(Grammar):
	grammar = (ONE_OR_MORE(Meta))
