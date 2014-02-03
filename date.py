import datetime
import dateutil.parser


def parse(date):
	try:
		dt = dateutil.parser.parse(date)
	except ValueError:
		dt = datetime.datetime(2997, 9, 12)
	except AttributeError:
		dt = None
	return dt
