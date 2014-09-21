
from collections import deque


def json_get(json_data, path):
	parts = deque(path[1:].split('/'))
	obj = json_data
	while len(parts) > 0:
		if obj is None:
			return None
		prop = parts.popleft()
		if prop not in obj:
			return None
		obj = obj[prop]
	return obj

def json_set(json_data, path, data):
	parts = deque(path[1:].split('/'))
	obj = json_data
	while len(parts) > 1:
		prop = parts.popleft()
		if prop not in obj:
			obj[prop] = {}
		obj = obj[prop]
	obj[parts[-1]] = data


class Values(object):
	def __init__(self, values = None):
		self.values = {} if values is None else values

	def get(self, path):
		return json_get(self.values, path)

	def set(self, path, data):
		json_set(self.values, path, data)
