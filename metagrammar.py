
from modgrammar import *


grammar_whitespace_mode = 'explicit'


class MetaError(Exception):
	def __init__(self, problem, text):
		self.problem = problem
		self.text = text
		
	def __str__(self):
		return "%s\nused in:\n%s" % (self.problem, self.text)
	
# class UnknownEnabler(MetaError):
	# def __init__(self, enabler, text):
		# MetaError.__init__(self, 'Unknown Enabler (SE/GE) "%s"' % enabler, text)
		
# class UnknownApplication(MetaError):
	# def __init__(self, app, text):
		# MetaError.__init__(self, 'Unknown application: "%s"' % app, text)

# class UnknownLocation(MetaError):
	# def __init__(self, loc, text):
		# MetaError.__init__(self, 'Unknown deployment location: "%s"' % loc, text)

# class UnknownPartner(MetaError):
	# def __init__(self, partner, text):
		# MetaError.__init__(self, 'Unknown partner: "%s"' % partner, text)

# class InvalidTimeframe(MetaError):
	# def __init__(self, problem, text):
		# MetaError.__init__(self, 'Invalid timeframe: "%s"' % problem, text)

		
class AmbiguousReference(MetaError):
	def __init__(self, ref, text):
		MetaError.__init__(self, 'Ambiguous reference: "%s"' % ref, text)


###############

class Identifier(Grammar):
	grammar = (WORD("[\w,\-!\&\(\)\/]", "[\w ,\-!\&\(\)\/]*", fullmatch=False, escapes=True, greedy=False))

class RedIdentifier(Grammar):
	grammar = (WORD("[\w]", "[\w \-!\(\)\/]*", fullmatch=False, escapes=True, greedy=False))

class AliasStmt(Grammar):
	grammar = (LITERAL("AS"), WHITESPACE, LIST_OF(RedIdentifier, sep=",", whitespace_mode='optional'))
	# grammar_whitespace_mode = 'required'
	# grammar_collapse = True

class ReferenceStmt(Grammar):
	grammar = (Identifier)

	def get_reference(self):
		return self.string

###############
	
class NamedEntityStmt(Grammar):
	# grammar = (LITERAL(    ), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AsStatement))
	# grammar_whitespace_mode = 'required'

	def get_identifier(self):
		return self.get(Identifier).string

	def get_aliases(self):
		aliasstmt = self.get(AliasStmt)
		if aliasstmt is None:
			return []
		return [alias.string for alias in aliasstmt.find_all(RedIdentifier)]

	def raise_ambiguity(self, id):
		raise AmbiguousReference(id, self.string)
	
	def check_unambiguity(self, data, id):
		if data.add_id(id):
			self.raise_ambiguity(id)
	
	def grammar_elem_init(self, data):
		self.check_unambiguity(data, self.get_identifier())
		for alias in self.get_aliases():
			self.check_unambiguity(data, alias)

###############


class GenericEnablerStmt(NamedEntityStmt):
	grammar = (LITERAL("GE"), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AliasStmt))

	
class LocationStmt(NamedEntityStmt):
	grammar = (LITERAL("LOC"), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AliasStmt))


class ScenarioStmt(NamedEntityStmt):
	grammar = (LITERAL("SCN"), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AliasStmt))


###############

class PartnerRef(ReferenceStmt):
	pass

class OriginatorStmt(Grammar):
	grammar = WHITESPACE, LITERAL("DEVELOPED") | LITERAL("PROVIDED") | LITERAL("CONDUCTED"), WHITESPACE, LITERAL("BY"), WHITESPACE, PartnerRef

	def get_partnername(self):
		return elem.get(PartnerRef).string


class EnablerRef(ReferenceStmt):
	pass









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
		LITERAL("USES") | LITERAL("WILL USE") | LITERAL("MAY USE"),
		OPTIONAL(TimeframeStmt),
		WHITESPACE,
		LIST_OF(EnablerRef, sep=",", whitespace_mode='optional')
	)
	
	def get_use_state(self):
		return self.elements[0].string
		
	def get_timing(self):
		return None # self.get(TimeframeStmt)
		
	def get_enablers(self):
		return [e.string for e in self.find_all(EnablerRef)]



	


class OriginatedEntityStmt(NamedEntityStmt):
	def get_originator(self):
		return self.get(OriginatorStmt).get_name()


class DependentEntityStmt(OriginatedEntityStmt):
	def get_dependencies(self):
		return self.get_uses() + self.get_will_use() + self.get_may_use()
	
	def get_uses(self):
		return self.handleUseStmts('USES')

	def get_will_use(self):
		return self.handleUseStmts('WILL USE')

	def get_may_use(self):
		return self.handleUseStmts('MAY USE')

	def handleUseStmts(self, state):
		result = []
		for u in self.find_all(UseStmt):
			if u.get_state() != state:
				continue
			
			timing = u.get_timing()
			# TODO:
			if timing is not None:
				# if usestate == "USES":
					# raise InvalidTimeframe("Timeframe for USES relation neither allowed nor necessary!")

				timing = validateTimeframe(timing.elements[3].string)
				# TODO: check return value
			# print(timeframe)
				
			enablers = u.get_enablers() # [e.string for e in u.elements[3].find_all(RedIdentifier)]
			
			result.extend([(state, e, timing) for e in enablers])
			# print(enablers)
			# l = [e for e in [data.enabler(e) for e in enablers] if e is not None]
			# for ename in enablers:
				# e = data.enabler(ename)
				# if e is None:
					# raise UnknownEnabler(ename, hint)
				# usestates[usestate].append(e)
				# timing[e] = timeframe
				# print('Enabler %s integrated by %s' % (e.identifier, timeframe))
		return result


class SpecificEnablerStmt(DependentEntityStmt):
	grammar = (
		LITERAL("SE"), WHITESPACE, Identifier,
		OPTIONAL(WHITESPACE, AliasStmt),
		OriginatorStmt,
		ZERO_OR_MORE(WHITESPACE, UseStmt)
	)


class ApplicationStmt(DependentEntityStmt):
	grammar = (
		LITERAL("APP"), WHITESPACE, Identifier,
		OPTIONAL(WHITESPACE, AliasStmt),
		OriginatorStmt,
		ONE_OR_MORE(WHITESPACE, UseStmt)
	)
	

###############



class Place(Grammar):
	grammar = (Identifier)

class Date(Grammar):
	grammar = (Identifier)

class ExperimentationSite(Grammar):
	grammar = (Identifier)

class ScenarioRef(ReferenceStmt):
	pass

class ApplicationRef(ReferenceStmt):
	pass


class DeploymentStmt(Grammar):
	grammar = (LITERAL("WITH"), WHITESPACE, LIST_OF(RedIdentifier, WHITESPACE, LITERAL("DEPLOYED"), WHITESPACE, LITERAL("AT"), WHITESPACE, RedIdentifier, sep=',', whitespace_mode='optional'))


class EXPERIMENT(Grammar):
	grammar = (
		LITERAL("EXPERIMENT"), WHITESPACE, LITERAL("IN"), WHITESPACE, Place,
		OPTIONAL(WHITESPACE, LITERAL("OF"), WHITESPACE, LITERAL("SITE"), WHITESPACE, ExperimentationSite),
		WHITESPACE, LITERAL("AT"), WHITESPACE, Date,
		OriginatorStmt,
		WHITESPACE, LITERAL("DRIVES"), WHITESPACE, ScenarioRef,
		ONE_OR_MORE(WHITESPACE, DeploymentStmt),
		WHITESPACE, LITERAL("BY"), WHITESPACE, LITERAL("RUNNING"), WHITESPACE, ApplicationRef
	)

	def grammar_elem_init2(self, data):
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


class MetaStmt(Grammar):
	grammar = (BOL, OR(
			GenericEnablerStmt,
			SpecificEnablerStmt,
			LocationStmt,
			ScenarioStmt,
			ApplicationStmt,
			EXPERIMENT, WHITESPACE, EMPTY
		), EOL)

class MetaStructureGrammar(Grammar):
	grammar = (ONE_OR_MORE(MetaStmt))
