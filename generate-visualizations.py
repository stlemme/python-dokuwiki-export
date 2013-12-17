

import re
from getpage import *


rx_code = re.compile(r"^((.*)(<code>)(.*)|(.*)(</code>).*)+")


def preprocess(meta):
	active = False
	output = []
	
	for line in meta:
		result = rx_code.findall(line)
		
		if not len(result):
			if active:
				output.append(line.strip())
			continue
		
		# print result
		
		for g in result:
			# active |= len(g[2])
			if len(g[2]):
				if active:
					print('Warning! <code> appears within meta structure description - ignored.')
					output.append('# invalid line:')
					output.append('# ' + line)
					output.append(g[1])
				active = True
			
			if active:
				output.append(g[3] + g[4])
				
			# active &= not len(g[5])
			if len(g[5]):
				if not active:
					print('Warning! </code> appears without meta structure description or twice - ignored.')
					output.append('# invalid line:')
					output.append('# ' + line)
				active = False

	return output


# rx_meta = {
	# 'GE' : re.compile(r"GE (.+)( AS (.+)(,\w*(.+))*)?\w+")
# }

# class Named(object):
	# def __init__(self, tree)
		# self.name = "name-from-tree"

# class Renameable(Named):
	# def __init__(self, tree)
		# Named.__init__(self, tree)
		# self.alias = []
		# visit parse tree
	
# class GE(Renameable):
	# def __init__(self, tree):
		# Renameable.__init__(self, tree)

# class LOC(Renameable):
	# def __init__(self, tree):
		# Renameable.__init__(self, tree)

# class Dependent(Renameable):
	# def __init__(self, tree):
		# Renameable.__init__(self, tree)
		# self.uses = []
		# self.willuse = []
		# self.mayuse = []
		
# class SE(Dependent):
	# def __init__(self, tree):
		# Dependent.__init__(self, tree)

# class APP(Dependent):
	# def __init__(self, tree):
		# Dependent.__init__(self, tree)

# class EXPERIMENT(object):
	# def __init__(self, tree):
		# self.site = ""
		# self.date = ""
		# self.scenario = ""
		# self.apps = []
		# self.deployment = []


from modgrammar import *

grammar_whitespace_mode = 'explicit'


class Identifier(Grammar):
	grammar = (WORD("[\w]", "[\w ,\-!\(\)]*", fullmatch=True, escapes=True))

class RedIdentifier(Grammar):
	grammar = (WORD("[\w\-]", fullmatch=True, escapes=True))
	
class AsStatement(Grammar):
	grammar = (LITERAL("AS"), LIST_OF(RedIdentifier, sep=","))

class GE(Grammar):
	grammar = (LITERAL("GE"), WHITESPACE, Identifier, OPTIONAL(WHITESPACE, AsStatement))

class Comment(Grammar):
	grammar = (LITERAL("#"), REST_OF_LINE)

class Meta(Grammar):
	grammar = (OR(GE, Comment, SPACE, EMPTY), EOL)

class MyGrammar(Grammar):
	grammar = (ONE_OR_MORE(Meta))

	
class metaprocessor:
	def __init__(self):
		self.ge = {}
		self.se = {}
		self.loc = {}
		
	def process(self, doc):
		p = MyGrammar.parser()
		
		text = '\n'.join(doc)
		
		try:
			# for l in doc:
				# result = p.parse_text(l + '\n')
				# if result is not None:
					# print(result.elements)
			result = p.parse_text(text, eof=True)
			if result is not None:
				print(result.elements)
		except ParseError as e:
			print('Parsing failed!')
			print(e)
		pass


if __name__ == "__main__":
	import sys
	
	metapage = ":FIcontent:private:meta:"
	if len(sys.argv) > 1:
		metapage = sys.argv[1]

	outfile = "generated-meta.txt"
	if len(sys.argv) > 2:
		outfile = sys.argv[2]

	meta = getpage(metapage)
	if meta is None:
		sys.exit("Error! Meta structure %s not found." % metapage)

	doc = preprocess(meta)
	
	print()
	print()
	# for l in doc:
		# print(l)

	mp = metaprocessor()
	mp.process(doc)

	print()
	print()
	print("GEs (%d):" % len(mp.ge))
	print("SEs (%d):" % len(mp.se))
	print("LOCs (%d):" % len(mp.loc))
	