
from getpage import *
from preprocess import *
from metaprocessor import *
import presenter

###############
	
def output(text):
	print(text)
	
def warning(text):
	output("[Warning] %s" % text)
	
def error(text):
	output("[Error] %s" % text)
	
###############


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
	meta = mp.process(doc)

	print()
	print()
	print("GEs (%d):" % len(mp.data.ge))
	print("SEs (%d):" % len(mp.data.se))
	print("LOCs (%d):" % len(mp.data.loc))
	
	tl = presenter.ExperimentTimelinePresenter()
	tl.present(meta)
	
	tl.dump(sys.stdout)
	
