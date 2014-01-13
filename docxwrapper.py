
from docx import docx
import logging


class docxwrapper:
	def __init__(self, template, imagepath=None):
		self.template = template
		self.pictures = []
		self.picturemap = {}
		self.references = {}
		
		if imagepath is None:
			self.imagepath = ""
		else:
			self.imagepath = imagepath
		
		self.doc, self.relationships = docx.opendocx(self.template)

		result = self.doc.xpath("/w:document/w:body/w:p[w:r/w:t[starts-with(.,'Replace Me')]]", namespaces=docx.nsprefixes)
		self.par = result[0]

		result = self.doc.xpath("/w:document/w:body/w:p[w:r/w:t[starts-with(.,'Replace Me2')]]", namespaces=docx.nsprefixes)
		if result is not None:
			self.refpar = result[0]
		else:
			logging.info("No references section")

	def insert(self, elem):
		if elem is None:
			return
		self.par.addprevious(elem)

	def insertpicture(self, picfile, caption, size=None, jc=None):
		# print picfile
		# check for a conversion
		if picfile in self.picturemap.keys():
			picfile = self.picturemap[picfile]
		# print picfile
		
		# check if it was already embedded
		other_rel = self.relationships.xpath("Relationship[@Target='media/%s']" % picfile)
		
		if len(other_rel) > 0:
			picrelid = other_rel[0].get('Id')
		else:
			picrelid = "rId" + str(len(self.relationships) + 1)

		# print "insertpicture:", picfile, picrelid, len(other_rel)
		
		picpara, newpicfile = docx.picture2(picrelid, picfile, self.imagepath, caption, pixelsize=size, document=self.doc, jc=jc)
		self.insert(picpara)
		
		# print "insertpicture - newpicfile:", newpicfile
		if newpicfile != picfile:
			self.picturemap[picfile] = newpicfile
			picfile = newpicfile
		
		# print self.picturemap
		
		if caption is not None:
			cappara = docx.imagecaption(caption, len(self.pictures) + 1, style="EUCaption")
			self.insert(cappara)
		
		# other_rel = self.relationships.xpath("Relationship[@Target='media/" + picfile + "']")
		# print "Relation:", picfile, len(other_rel)
		if len(other_rel) > 0:
			return

		rel_elm = docx.makeelement('Relationship', nsprefix=None, attributes={
			'Id':     picrelid,
			'Type':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
			'Target': 'media/' + picfile
		})
		self.relationships.append(rel_elm)
		self.pictures.append(picfile)

		# print "Inserted"
		
		
		# caption = 'Figure ' + str(len(self.pictures)) + ' ' + caption
		# self.insert(docx.paragraph(caption, style='EUCaption'))
		
	def lookupref(self, ref, target):
		if ref not in self.references.keys():
			self.refpar.addprevious(docx.paragraph(target, style='EUReference'))
			self.references[ref] = len(self.references) + 1
		return self.references[ref]
		
	def pagecontentsize(self):
		return docx.pagecontentsize(self.doc)
		
	def cleanup(self):
		result = self.doc.xpath("/w:document/w:body", namespaces=docx.nsprefixes)
		if result is None:
			return
		body = result[0]
		body.remove(self.par)
		body.remove(self.refpar)
		self.par = None

	def generate(self, outfile):
		self.cleanup()
		docx.updatedocx(self.doc, self.pictures, self.relationships, self.imagepath, self.template, outfile)

