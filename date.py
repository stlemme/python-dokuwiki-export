import datetime
import dateutil.parser


some_date_in_far_future = datetime.date(2997, 9, 12)

def parse(date):
	if date is None:
		return some_date_in_far_future
	
	if date.lower() in ['asap', 'urgent', 'today']:
		return datetime.date.today()

	try:
		dt = dateutil.parser.parse(date)
		return datetime.date(dt.year, dt.month, dt.day)
	except ValueError:
		return some_date_in_far_future
	except AttributeError:
		# print(date)
		return some_date_in_far_future

	return some_date_in_far_future
