
tags = set([
	'Connected TV', 'Second Screen', 'Multimedia data analysis', 'Speech to Text', 'Social Networks', 'Smart City Services', 'Geo-localization', 'Geographical Information System', 'Point of Interest', 'Recommendation System', 'Open Data', 'App Development Tool', 'Mobile Services', 'User Interface Generator', 'Document Processing', 'Information Mashup', 'Augmented Reality', 'Gaming', 'Pervasive Gaming', 'User interface', '3D User Interface', 'Animated Characters', 'Game development tool', 'Text to Speech',
	
	'Geospatial', '3D graphics', '3D', 'Text and Speech', 'POI', 'Smart City', 'Recommendation', 'Social',
	
	'Mobile', 'Android', 'iOS', 'WebUI', 'Unity', 'XML3D',
	
	'Open software', 'SaaS service', 'Client side', 'Server side'
])


import logging
import urllib.request


def get_url_status(url):
	if url is None:
		return False
	try:
		r = urllib.request.urlopen(url)
		return r.status == 200
	except urllib.error.HTTPError as e:
		logging.info('Error: %s' % e)
	except Exception as e:
		logging.warning('Error: %s' % e)
	return False

def check_remote_resource(url, msg = None):
	logging.info('Checking remote resource at %s' % url)
	if get_url_status(url):
		return True
	if msg is not None:
		logging.warning(msg)
	return False
