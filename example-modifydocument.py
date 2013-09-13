#!/usr/bin/env python

"""
This file makes a .docx (Word 2007) file from scratch, showing off most of the
features of python-docx.

If you need to make documents from scratch, you can use this file as a basis
for your work.

Part of Python's docx module - http://github.com/mikemaccana/python-docx
See LICENSE for licensing information.
"""

from docx import docx
from docxwrapper import *


if __name__ == '__main__':

	templatefile = 'template.docx'
	generatefile = 'generated.docx'
	imagepath = "myimages/"
	
	document = docxwrapper(templatefile, imagepath)

	
	document.insert(docx.heading("I'm a new heading", 1))
	document.insert(docx.paragraph("text ewfawgeawaw etagwa way awy aewyj4 jjs rse " * 20))
	document.insert(docx.paragraph("aksdjg wagnlgbg weagbwli gbasigb ibigb regae heerah eahe3 hheah " * 15))
	document.insert(docx.heading("I'm a second new heading", 1))
	document.insert(docx.paragraph("aksdjg wagnlgbg weagbwli gbasigb ibigb regae heerah eahe3 hheah " * 15))
	document.insertpicture('imagepy.png', 'This is a test description')
	document.insert(docx.paragraph("aksdjg wagnlgbg weagbwli gbasigb ibigb regae heerah eahe3 hheah " * 15))
	document.insertpicture('2.png', 'This is a test description')
	document.insert(docx.paragraph("aksdjg wagnlgbg weagbwli gbasigb ibigb regae heerah eahe3 hheah " * 15))
	

	
	document.generate(generatefile)
