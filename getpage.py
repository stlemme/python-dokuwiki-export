
def readfile(filename):
	try:
		fo = open(filename, "r")
		content = fo.readlines()
		fo.close()
	except IOError:
		content = None
	return content


ns_delimiter = ":"
default_ns_page = "start"


def resolve(page, rel_ns = []):
	parts = page.split(ns_delimiter)

	# a page in the same namespace
	if len(parts) == 1:
		return rel_ns + page;
	
	# referring to a namespace rather than a page
	if len(parts[-1]) == 0:
		parts[-1] = default_ns_page

	# referring to global namespace
	if len(parts[0]) == 0:
		path = []
		parts = parts[1:]
	else:
		path = rel_ns[:]
	
	trail = 0
	for ns in parts[:-1]:
		if ns == '..':
			#parent
			trail += 1
			path.pop()
		elif ns == '.':
			#current
			trail += 1
		else:
			break
	
	path = path + parts[trail:]
	return ':' + ':'.join(path)
	

def getpage(page, ns = []):
	# this could be replaced to utilize the dokuwiki xml-rpc
	fullname = resolve(page, ns)
	filename = fullname.replace(':', '/').lower()
	# print 'getpage(%s, %s) => %s - %s' % (page, ns, fullname, filename)
	return readfile('pages' + filename + ".txt")

