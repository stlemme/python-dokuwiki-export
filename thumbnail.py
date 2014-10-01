
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from collections import deque


margin = 35
font_color_code = "#000000"
font_family = "verdana.ttf" # "sans-serif.ttf"
font_size = 50
line_height = 60


def HTMLColorToPILColor(colorstring):
    """ converts #RRGGBB to PIL-compatible integers"""
    colorstring = colorstring.strip()
    while colorstring[0] == '#': colorstring = colorstring[1:]
    # get bytes in reverse order to deal with PIL quirk
    colorstring = colorstring[-2:] + colorstring[2:4] + colorstring[:2]
    # finally, make it numeric
    color = int(colorstring, 16)
    return color


def generate_thumb(filename, bgcolor_code, text, size):
	bgcolor = HTMLColorToPILColor(bgcolor_code)
	
	img = Image.new("RGB", size, color=bgcolor)
	draw = ImageDraw.Draw(img)

	# font = ImageFont.truetype(<font-file>, <font-size>)
	font = ImageFont.truetype(font_family, font_size)

	textparts = text.split(" ")
	lines = deque()

	for t in textparts:
		try:
			c = lines.pop()
			p = c + " " + t
		except IndexError:
			p = t
		
		s = draw.textsize(p, font=font)
		# print(s)
		
		if s[0]+2*margin < size[0]:
			lines.append(p)
		else:
			lines.append(c)
			lines.append(t)

	offset_y = (size[1] - len(lines)*line_height) / 2
	
	font_color = HTMLColorToPILColor(font_color_code)
	
	for i, l in enumerate(lines):
		s = draw.textsize(l, font=font)
		pos = (size[0] - s[0]) / 2, offset_y + i*line_height + (line_height-s[1])/2
		draw.text(pos, l, font_color, font=font)

	img.save(filename)



if __name__ == '__main__':
	import sys
	
	size = 460, 345
	bgcolor = "#FF8800"
	filename = 'thumb.png'

	if len(sys.argv) < 2:
		sys.exit('Usage: %s "Text to be drawn" [ #FF8800 [ thumb.png ] ]' % sys.argv[0])
	
	text = sys.argv[1]
		
	if len(sys.argv) > 2:
		bgcolor = sys.argv[2]

	if len(sys.argv) > 3:
		filename = sys.argv[3]

	generate_thumb(filename, bgcolor, text, size)
