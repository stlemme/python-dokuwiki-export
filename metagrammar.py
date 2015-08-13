
from modgrammar import *
import logging


grammar_whitespace_mode = 'explicit'


class MetaError(Exception):
	def __init__(self, problem, text):
		self.problem = problem
		self.text = text
		
	def __str__(self):
		return "%s\nused in:\n%s" % (self.problem, self.text)
	
class AmbiguousReference(MetaError):
	def __init__(self, ref, text):
		MetaError.__init__(self, 'Ambiguous symbol: "%s"' % ref, text)


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
	def get_keyword(self):
		return self.elements[0].string

	def get_identifier(self):
		return self.get(Identifier).string

	def get_aliases(self):
		aliasstmt = self.find(AliasStmt)
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

	def get_name(self):
		return self.get(PartnerRef).string


class EnablerRef(ReferenceStmt):
	pass









# TODO: restrict to any type of date (M12, Release 06/14, February 2014)
class PointInTime(Grammar):
	grammar = (WORD("[\w]", "[\w \(\)\/]*", fullmatch=False, escapes=True, greedy=False))
	
class TimeframeStmt(Grammar):
	grammar = (WHITESPACE, LITERAL("FROM"), WHITESPACE, PointInTime, WHITESPACE, LITERAL("ON"))
	
	def get_date(self):
		return self.get(PointInTime).string
	
# import date

# def validateTimeframe(pit):
	# TODO: validate against various regexp, fuzzy date parsing, etc.
	# TODO: store respective datetime object
	# tf = date.parseProjectDate(pit)
	# if tf < date.projectbegin or tf > date.projectend:
		# logging.warning("Timeframe outside of project course: %s (%s)" % (pit, tf))
	# return (pit, tf)


class UseStmt(Grammar):
	grammar = (
		LITERAL("USES") | LITERAL("WILL USE") | LITERAL("MAY USE"),
		OPTIONAL(TimeframeStmt),
		WHITESPACE,
		LIST_OF(EnablerRef, sep=",", whitespace_mode='optional')
	)
	
	def get_state(self):
		return self.elements[0].string
		
	def get_timing(self):
		tf = self.find(TimeframeStmt)
		if tf is None:
			return None
		return tf.get_date()
		
	def get_enablers(self):
		return [e.string for e in self.find_all(EnablerRef)]


	def grammar_elem_init(self, data):
		if self.get_state() == 'USES':
			return
		
		tf = self.find(TimeframeStmt)
		if tf is None:
			logging.info("For upcoming usage information (WILL/MAY USE) an information on the time frame is expected.")
		



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
			enablers = u.get_enablers()
			
			result.extend([(state, e, timing) for e in enablers])

		return result

class WikiPageStmt(Grammar):
	grammar = (WORD(":", "\w:", escapes=True))

class DescriptionPageStmt(Grammar):
	grammar = (LITERAL("DESCRIBED"), WHITESPACE, LITERAL("AT"), WHITESPACE, WikiPageStmt)
	
	def get_wiki_page(self):
		return self.get(WikiPageStmt).string

class DeprecatedStmt(Grammar):
	grammar = (LITERAL("DEPRECATED"))
	
class SEKeywordStmt(Grammar):
	grammar = OPTIONAL(DeprecatedStmt, WHITESPACE), LITERAL("SE")

class SpecificEnablerStmt(DependentEntityStmt):
	grammar = (
		SEKeywordStmt, WHITESPACE, Identifier,
		OPTIONAL(WHITESPACE, AliasStmt),
		OriginatorStmt,
		OPTIONAL(WHITESPACE, DescriptionPageStmt),
		ZERO_OR_MORE(WHITESPACE, UseStmt)
	)

	def get_meta_page(self):
		desc = self.find(DescriptionPageStmt)
		# print(desc)
		if desc is None:
			return None
		return desc.get_wiki_page()
		
	def is_deprecated(self):
		return self.find(DeprecatedStmt) is not None


class ApplicationStmt(DependentEntityStmt):
	grammar = (
		LITERAL("APP"), WHITESPACE, Identifier,
		OPTIONAL(WHITESPACE, AliasStmt),
		OriginatorStmt,
		ONE_OR_MORE(WHITESPACE, UseStmt)
	)
	

###############

class ExperimentationSite(Grammar):
	grammar = (
		LITERAL("Barcelona") |
		LITERAL("Berlin") |
		LITERAL("Brittany") |
		LITERAL("Cologne") |
		LITERAL("Zurich") |
		LITERAL("Lancaster")
	)

class Place(Grammar):
	grammar = (Identifier)


class ExperimentLocationStmt(Grammar):
	grammar = (WHITESPACE, LITERAL("IN"), WHITESPACE, OR(
		ExperimentationSite,
		(Place, WHITESPACE, LITERAL("OF"), WHITESPACE, LITERAL("SITE"), WHITESPACE, ExperimentationSite)
	))
	
	def get_site(self):
		return self.find(ExperimentationSite).string
		
	def get_place(self):
		p = self.find(Place)
		if p is None:
			return None
		return p.string
	

class DateStmt(Grammar):
	grammar = (Identifier)


class ScenarioRef(ReferenceStmt):
	pass

class ApplicationRef(ReferenceStmt):
	pass

class LocationRef(ReferenceStmt):
	pass


class DeploymentStmt(Grammar):
	grammar = (EnablerRef, WHITESPACE, LITERAL("DEPLOYED"), WHITESPACE, LITERAL("AT"), WHITESPACE, LocationRef)
	
	def get_enabler(self):
		return self.get(EnablerRef).string
		
	def get_location(self):
		return self.get(LocationRef).string


class MultiDeploymentStmt(Grammar):
	grammar = (LITERAL("WITH"), WHITESPACE, LIST_OF(DeploymentStmt, sep=',', whitespace_mode='optional'))


class ExperimentStmt(Grammar):
	grammar = (
		LITERAL("EXPERIMENT"), ExperimentLocationStmt,
		WHITESPACE, LITERAL("AT"), WHITESPACE, DateStmt,
		OriginatorStmt,
		WHITESPACE, LITERAL("DRIVES"), WHITESPACE, ScenarioRef,
		ONE_OR_MORE(WHITESPACE, MultiDeploymentStmt),
		WHITESPACE, LITERAL("BY"), WHITESPACE, LITERAL("RUNNING"), WHITESPACE, ApplicationRef
	)
	
	def get_site(self):
		return self.get(ExperimentLocationStmt).get_site()
		
	def get_place(self):
		return self.get(ExperimentLocationStmt).get_place()

	def get_originator(self):
		return self.get(OriginatorStmt).get_name()

	def get_date(self):
		return self.get(DateStmt).string
	
	def get_scenario(self):
		return self.get(ScenarioRef).string
	
	def get_application(self):
		return self.get(ApplicationRef).string
	
	def get_deployments(self):
		return dict([(dstmt.get_enabler(), dstmt.get_location()) for dstmt in self.find_all(DeploymentStmt)])


###############

class ReleaseNameStmt(Grammar):
	grammar = (WORD("[0-9]{2}"), LITERAL("/"), WORD("[0-9]{2}"))

class ReleaseStmt(Grammar):
	grammar = (
		LITERAL("RELEASE"), WHITESPACE, ReleaseNameStmt, WHITESPACE, LITERAL("CONTAINS"), WHITESPACE,
		LIST_OF(EnablerRef, sep=',', whitespace_mode='optional')
	)

	def get_release_name(self):
		return self.get(ReleaseNameStmt).string

	def get_content(self):
		return [ref.string for ref in self.find_all(EnablerRef)]


###############


class MetaStmt(Grammar):
	grammar = (BOL, OR(
			GenericEnablerStmt,
			SpecificEnablerStmt,
			LocationStmt,
			ScenarioStmt,
			ApplicationStmt,
			ExperimentStmt,
			ReleaseStmt,
			
			WHITESPACE,
			EMPTY
		), EOL)

class MetaStructureGrammar(Grammar):
	grammar = (ONE_OR_MORE(MetaStmt))
