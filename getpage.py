
def readfile(filename):
	try:
		fo = open(filename, "r")
		content = fo.readlines()
		fo.close()
	except IOError:
		content = None
	return content


def getpage(page):
	# this could be replaced to utilize the dokuwiki xml-rpc
	return readfile("data/pages/" + page.lower() + ".txt")
