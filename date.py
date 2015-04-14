import datetime
import dateutil.parser


some_date_in_far_future = datetime.date(2997, 9, 12)

projectbegin = datetime.date(2013, 4, 1)
projectend = datetime.date(2015, 10, 31)


def today():
	return datetime.date.today()


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
	return parseProjectDateNew(date)

def parseProjectDateOld(date):
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
		month = int(result.group(1)) + 1
		year = 2000 + int(result.group(2))
		if month > 12:
			year += 1
			month -= 12
		return datetime.date(year, month, 1) - datetime.timedelta(days=1)
	
	print('Unable to parse project date: %s' % date)
	return None


class delta(object):
	def __init__(self, years = 0, months = 0, days = 0):
		self.years = int(years)
		self.months = int(months)
		self.days = int(days)
		
	def __radd__(self, other):
		m = other.month + self.months - 1
		y = other.year + self.years + (m//12)
		m = (m%12) + 1
		return datetime.date(y, m, other.day) + datetime.timedelta(days=self.days)
		
	def __rsub__(self, other):
		return other + delta(-self.years, -self.months, -self.days)

	
def parseProjectDateNew(date):
	result = rx_pm.match(date)
	if result is not None:
		month = int(result.group(1))
		d = projectbegin + delta(months=month) - delta(days=1)
		# print(d)
		return d
		
	result = rx_release.match(date)
	if result is not None:
		month = int(result.group(1))
		year = 2000 + int(result.group(2))
		d = datetime.date(year, month, 1) + delta(months=1) - delta(days=1)
		# print(d)
		return d
	
	print('Unable to parse project date: %s' % date)
	return None
