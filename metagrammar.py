
from modgrammar import *


grammar_whitespace_mode = 'explicit'


class MetaError(Exception):
	def __init__(self, problem, text):
		self.problem = problem
		self.text = text
		
	def __str__(self):
		return "%s\nused in:\n%s" % (self.problem, self.text)
	
	
###############

class Identifier(Grammar):
	grammar = (WORD("[\w]", "[\w ,\-!\&\(\)\/]*", fullmatch=False, escapes=True, greedy=False))

class RedIdentifier(Grammar):
	grammar = (WORD("[\w]", "[\w \-!\(\)\/]*", fullmatch=False, escapes=True))
	
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

class UseStmt(Grammar):
	grammar = (
		OR(
			LITERAL("USES"),
			LITERAL("WILL USE"),
			LITERAL("MAY USE")
		),
		WHITESPACE,
		LIST_OF(RedIdentifier, sep=",", whitespace_mode='optional')
	)
	
def handleUseStmts(stmts, usestates, data):
	for u in stmts.find_all(UseStmt):
		usestate = u.elements[0].string
		enablers = [e.string for e in u.elements[2].find_all(RedIdentifier)]
		l = [e for e in [data.enabler(e) for e in enablers] if e is not None]
		usestates[usestate] += l

class SE(NamedEntity):
	grammar = (
		LITERAL("SE"), WHITESPACE, Identifier,
		OPTIONAL(WHITESPACE, AsStatement),
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
		
		if self.elements[4] is not None:
			handleUseStmts(self.elements[4], self.usestates, data)


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
		
		if self.elements[4] is not None:
			handleUseStmts(self.elements[4], self.usestates, data)


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
		LITERAL("EXPERIMENT"), WHITESPACE, LITERAL("IN"), WHITESPACE, Place, WHITESPACE,
		OPTIONAL(LITERAL("OF"), WHITESPACE, LITERAL("SITE"), WHITESPACE, ExperimentationSite, WHITESPACE),
		LITERAL("AT"), WHITESPACE, Date, WHITESPACE,
		LITERAL("DRIVES"), WHITESPACE, Scenario, WHITESPACE,
		ONE_OR_MORE(DeploymentStmt, WHITESPACE),
		LITERAL("BY"), WHITESPACE, LITERAL("RUNNING"), WHITESPACE, Identifier
	)

	def grammar_elem_init(self, data):
		self.place = self.elements[4].string
		self.site = self.place
		if self.elements[6] is not None:
			self.site = self.elements[6].elements[4].string
			
		self.date = self.elements[9].string
		self.scenario = self.elements[13].string
		
		self.application = data.application(self.elements[20].string)
		if self.application is None:
			raise MetaError("Unknown application: %s" % self.elements[20].string, self.string)
		
		# TODO: extract deployment information


###############

class Meta(Grammar):
	grammar = (BOL, OR(GE, SE, LOC, APP, EXPERIMENT, WHITESPACE, EMPTY), EOL)

class MyGrammar(Grammar):
	grammar = (ONE_OR_MORE(Meta))