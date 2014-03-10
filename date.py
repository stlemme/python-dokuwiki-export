import datetime
import dateutil.parser


some_date_in_far_future = datetime.date(2997, 9, 12)

projectbegin = datetime.date(2013, 4, 1)
projectend = datetime.date(2015, 3, 31)

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

	
import re
	
rx_pm = re.compile('M([0-9]+)')
rx_release = re.compile('Release ([0-9]{2})/(13|14|15)')

def parseProjectDate(date):
	result = rx_pm.match(date)
	if result is not None:
		month = 4 + int(result.group(1))
		year = 2013
		while month > 12:
			year += 1
			month -= 12
		return datetime.date(year, month, 1) - datetime.timedelta(days=1)
		
	result = rx_release.match(date)
	if result is not None:
		return datetime.date(2000 + int(result.group(2)), int(result.group(1)) + 1, 1) - datetime.timedelta(days=1)
	
	print('Unable to parse project date: %s' % date)
	return None
		
		