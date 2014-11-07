
from collections import deque


def split_path(path):
	return deque(path.strip('/').split('/'))

def json_get(json_data, path):
	parts = split_path(path)
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
	parts = split_path(path)
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
		obj = json_get(self.values, path)
		if isinstance(obj, dict):
			obj = Values(obj)
		return obj

	def set(self, path, data):
		if isinstance(data, Values):
			data = data.values
		json_set(self.values, path, data)
