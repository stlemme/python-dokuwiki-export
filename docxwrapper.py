
from docx import docx

class docxwrapper:
	def __init__(self, template, imagepath=None):
		self.template = template
		self.pictures = []
		if imagepath is None:
			self.imagepath = ""
		else:
			self.imagepath = imagepath
		
		self.doc, self.relationships = docx.opendocx(self.template)

		result = self.doc.xpath("/w:document/w:body/w:p[w:r/w:t[starts-with(.,'Replace Me')]]", namespaces=docx.nsprefixes)
		self.par = result[0]

	def insert(self, elem):
		if elem is None:
			return
		self.par.addprevious(elem)

	def insertpicture(self, picfile, caption, size=None):
		picrelid = "rId" + str(len(self.relationships) + 1)

		picpara, picfile = docx.picture2(picrelid, picfile, self.imagepath, caption, pixelsize=size, document=self.doc)
		self.insert(picpara)
		# print "insertpicture - picfile:", picfile
		
		other_rel = self.relationships.xpath("Relationship[@Target='media/" + picfile + "']")
		# print "Relation:", picfile, len(other_rel)

		if len(other_rel) > 0:
			return
		
		# print "Inserted"
		
		rel_elm = docx.makeelement('Relationship', nsprefix=None, attributes={
			'Id':     picrelid,
			'Type':   'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image',
			'Target': 'media/' + picfile
		})
		self.relationships.append(rel_elm)
		self.pictures.append(picfile)
		
		
	def cleanup(self):
		result = self.doc.xpath("/w:document/w:body", namespaces=docx.nsprefixes)
		if result is None:
			return
		body = result[0]
		body.remove(self.par)
		self.par = None

	def generate(self, outfile):
		self.cleanup()
		docx.updatedocx(self.doc, self.pictures, self.relationships, self.imagepath, self.template, outfile)

