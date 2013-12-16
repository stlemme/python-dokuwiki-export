

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
					print "Warning! <code> appears within meta structure description - ignored."
					output.append("# invalid line:")
					output.append("# " + line)
					output.append(g[1])
				active = True
			
			if active:
				output.append(g[3] + g[4])
				
			# active &= not len(g[5])
			if len(g[5]):
				if not active:
					print "Warning! </code> appears without meta structure description or twice - ignored."
					output.append("# invalid line:")
					output.append("# " + line)
				active = False

	return output


rx_meta = [
	re.compile(r"GE (.*) AS (.*)(,\w*(.*))")
]
	
class metaprocessor:
	def __init__(self):
		self.ge = {}
		self.se = {}
		self.loc = {}

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
	
	print
	print
	for l in doc:
		print l

	# fo = open(outfile, "w")
	# fo.writelines(doc)
	# fo.close()

	# if len(sys.argv) > 3:
		# chapterfile = sys.argv[3]

		# import json
		# with open(chapterfile, 'w') as cf:
			# json.dump(chapters, cf, sort_keys = False, indent = 4)

