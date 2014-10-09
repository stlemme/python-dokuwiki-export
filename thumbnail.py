
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from collections import deque


default_size = 460, 345

default_config = {
	'margin': 20,
	'font': {
		'color': "#000000",
		'family': "verdana.ttf", # "sans-serif.ttf"
		'size': 50
	},
	'line_height': 65
}


class ThumbnailGenerator(object):
	def __init__(self, size = default_size, config = default_config):
		self.config = config
		self.size = size

		# font = ImageFont.truetype(<font-file>, <font-size>)
		self.font = ImageFont.truetype(
			self.config['font']['family'],
			self.config['font']['size']
		)

		self.font_color = self.HTMLColorToPILColor(self.config['font']['color'])
		
		
	def HTMLColorToPILColor(self, colorstring):
		""" converts #RRGGBB to PIL-compatible integers"""
		colorstring = colorstring.strip()
		while colorstring[0] == '#': colorstring = colorstring[1:]
		# get bytes in reverse order to deal with PIL quirk
		colorstring = colorstring[-2:] + colorstring[2:4] + colorstring[:2]
		# finally, make it numeric
		color = int(colorstring, 16)
		return color


	def generate_thumb(self, filename, bgcolor_code, text):
		bgcolor = self.HTMLColorToPILColor(bgcolor_code)
		
		img = Image.new("RGB", self.size, color=bgcolor)
		draw = ImageDraw.Draw(img)

		textparts = text.split(" ")
		lines = deque()
		
		margin = self.config['margin']

		for t in textparts:
			try:
				c = lines.pop()
				p = c + " " + t
			except IndexError:
				c = None
				p = t
			
			s = draw.textsize(p, font=self.font)
			# print(s)
			
			if s[0]+2*margin < self.size[0]:
				lines.append(p)
			else:
				if c is not None:
					lines.append(c)
				lines.append(t)

		line_height = self.config['line_height']
		font_height = self.config['font']['size']
		line_count = len(lines)
		
		# if line_count % 2 == 0:
		offset_y = (self.size[1] - line_count*line_height + (line_height - font_height)) / 2
		# else:
			# middle = int(line_count/2)
			# s = draw.textsize(lines[middle], font=self.font)
			# offset_y = (self.size[1] - (line_count-1)*line_height - s[1]) / 2

		
		for i, l in enumerate(lines):
			s = draw.textsize(l, font=self.font)
			pos = (self.size[0] - s[0]) / 2, offset_y + i*line_height
			draw.text(pos, l, self.font_color, font=self.font)

		img.save(filename)



if __name__ == '__main__':
	import sys
	
	bgcolor = "#FF8800"
	filename = 'thumb.png'

	if len(sys.argv) < 2:
		sys.exit('Usage: %s "Text to be drawn" [ #FF8800 [ thumb.png ] ]' % sys.argv[0])
	
	text = sys.argv[1]
	
	thumbGen = ThumbnailGenerator()
		
	if len(sys.argv) > 2:
		bgcolor = sys.argv[2]

	if len(sys.argv) > 3:
		filename = sys.argv[3]

	thumbGen.generate_thumb(filename, bgcolor, text)
