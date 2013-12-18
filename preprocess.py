
import re

rx_code = re.compile(r"^((.*)(<code>)(.*)|(.*)(</code>).*)+")

def preprocess(meta):
	active = False
	output = []
	
	for line in meta:
		result = rx_code.findall(line)
		
		if not len(result):
			# remove comments
			if line.lstrip().startswith('#'):
				continue
				
			if active:
				output.append(line.strip())
			continue
		
		# print result
		
		for g in result:
			# active |= len(g[2])
			if len(g[2]):
				if active:
					print('Warning! <code> appears within meta structure description - ignored.')
					# output.append('# invalid line:')
					# output.append('# ' + line)
					output.append(g[1])
				active = True
			
			if active:
				output.append(g[3] + g[4])
				
			# active &= not len(g[5])
			if len(g[5]):
				if not active:
					print('Warning! </code> appears without meta structure description or twice - ignored.')
					# output.append('# invalid line:')
					# output.append('# ' + line)
				active = False

	return output