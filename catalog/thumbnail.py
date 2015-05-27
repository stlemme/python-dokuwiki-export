
import logging
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
# from collections import deque
from io import BytesIO

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

		s = img.size
		if int(round(100 * s[1] / s[0])) != 75:
			logging.warning("Thumbnail dimensions do not match 4:3")
			return False
			
		if s[0] < self.size[0]:
			logging.warning("The input image has a smaller resolution than the desired output thumbnail.")
		
		img.thumbnail(self.size)
		
		try:
			img.save(filename, optimize=True)
		except IOError:
			logging.warning("Cannot create thumbnail %s" % filename)
			return False

		return True
