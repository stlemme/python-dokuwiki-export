
import logging
import re
from jsonutils import Values


class ProcessingGenerator(object):
	
	whitespaces = re.compile('[\t\n]+')
	
	def __init__(self, escaping = lambda t : t):
		self.se = None
		self.escape = escaping
	
	
	# stack = 0
	
	def process_text_snippet(self, text, trim_whitespaces=False):
		# print('  ' * self.stack, text.encode('ascii', 'replace'))
		# self.stack += 1
		
		try:
			# print('a')
			text = self.rx_for.sub(self.handle_for, text)
			# print('b')
			text = self.rx_if.sub(self.handle_condition, text)
			# print('c')
			text = self.rx_value.sub(self.handle_value, text)
		except TypeError as e:
			print(text);
			print(e);
			text = ""
		# self.stack -= 1
		if trim_whitespaces:
			text = self.whitespaces.sub('', text)
		return text

	
	def process_value(self, path):
		val = self.se.get(path)
		if val is None:
			logging.warning('Undefined property %s' % path)
			return "[[UNDEFINED]]"
		
		# print(val)
		val = self.escape(val)
		return self.process_text_snippet(val)
		
	rx_value = re.compile(r'\{\{(/[a-zA-Z\-/]+)\}\}')

	def handle_value(self, match):
		path = match.group(1)
		# print(path)
		return self.process_value(path)

		
	rx_for = re.compile(r'\{\{for (/[a-zA-Z\-/]+)\}\}([ \t\f\v]*\n)?(.+?)\{\{endfor\}\}([ \t\f\v]*\n)?', re.DOTALL)

	def handle_for(self, match):
		# print(match.group())
		path = match.group(1)
		repl = match.group(3)
		# print(path)
		val = self.se.get(path)
		if val is None:
			return ""
		text = ""

		if isinstance(val, list):
			items = enumerate(val)
		else:
			items = val.items()

		for k, v in items:
			# print(k, '  --  ', v)
			current = re.sub(r'%value(/[a-zA-Z0-9\-/]+)?%', lambda m: self.handle_item_value(v, m), repl)
			text += self.process_text_snippet(current)
		
		return text

	def handle_item_value(self, item, match):
		if match.group() == '%value%':
			return str(item)
		path = match.group(1)
		# print(path)

		val = None
		if isinstance(item, Values):
			val = item.get(path)
		if isinstance(item, dict):
			val = item[path]

		if val is None:
			logging.warning('Undefined property %s of item' % path)
			val = "[[UNDEFINED]]"
		# print(val)
		val = self.escape(val)
		return val

	rx_if = re.compile(r'\{\{if (/[a-zA-Z\-/]+) (!=|==) "([^\"]*)"\}\}([ \t\f\v]*\n)?(.+?)\{\{endif\}\}([ \t\f\v]*\n)?', re.DOTALL)

	def handle_condition(self, match):
		# print(match.group())
		path = match.group(1)
		op = match.group(2)
		compare = match.group(3)
		repl = match.group(5)

		val = self.se.get(path)
		if val is None:
			val = ""
		
		if op == '==' and val != compare:
			return ""
			
		if op == '!=' and val == compare:
			return ""

		return self.process_text_snippet(repl)
