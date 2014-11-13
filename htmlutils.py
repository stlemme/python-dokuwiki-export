

from html import escape, entities
import re


def basic_html_escaping(text):
	return escape(text)


def html_entity_from_char(char):
	cp = ord(char)
	if cp in entities.codepoint2name:
		return '&%s;' % entities.codepoint2name[cp]
	if cp > 127:
		return '&#%s;' % cp
	return char

def char_from_html_entity(entity):
	name = entity.strip('&;')
	if name.startswith('#'):
		return chr(int(name[1:], 16))
	if name in entities.name2codepoint:
		return chr(entities.name2codepoint[name])
	# TODO: raise exception of unknown named entity
	return '?'


def encode_to_html_entities(text):
	s = [html_entity_from_char(c) for c in text]
	return ''.join(s)

def decode_from_html_entities(text):
	convert = lambda match : char_from_html_entity(match.group())
	return re.sub(r'&(#[0-9a-fA-F]+|[a-zA-Z]+);', convert, text)

def html_named_entity_escaping(text):
	text = decode_from_html_entities(text)
	return encode_to_html_entities(text)

def non_ascii_escaping(text):
	return text.encode('ascii', 'xmlcharrefreplace').decode('ascii')

def no_escaping(text):
	return text
