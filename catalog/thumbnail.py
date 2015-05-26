
import logging
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
# from collections import deque
from io import BytesIO
from math import floor

default_size = 460, 345

default_config = {
}


class ThumbnailGenerator(object):
	def __init__(self, dw, size = default_size, config = default_config):
		self.dw = dw
		self.config = config
		self.size = size

	def generate_thumb(self, thumbname, filename):
		file = self.dw.getfile(thumbname)
		if file is None:
			logging.warning("Could not retrieve thumbnail %s from wiki." % thumbname)
			return False
		
		buffer = BytesIO(file)
		img = Image.open(buffer)

		# img.save('org_' + filename)

		s = img.size
		if floor(100 * s[1] / s[0]) != 75:
			logging.warning("Thumbnail dimensions do not match 4:3")
			return False
		
		img.thumbnail(self.size)
		
		try:
			img.save(filename, optimize=True)
		except IOError:
			logging.warning("Cannot create thumbnail %s" % filename)
			return False

		return True
