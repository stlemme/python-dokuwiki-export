#!/usr/bin/env python
# coding: utf8

from docx import docx
from docxwrapper import docxwrapper

import urllib2
import re

type(docx)

chapters = {}
# chapters["FIcontent.SmartCity.Architecture"] = {"chapter": "4.1", "title": "SCG"}
# chapters["FIcontent.Common.Enabler.SocialNetwork"] = {"chapter": "4.2", "title": "SNE"}


def replaceLinks(c):
    if not "[[" in c:
        return c
    else:

        r1 = "\[\[(([^\]|]|\](?=[^\]]))*)(\|(([^\]]|\](?=[^\]]))*))?\]\]"

        for m in re.finditer(r1, c):
            # print '%02d-%02d: %s' % (m.start(), m.end(), m.group(0))
            found = m.group(0)
            s = found[2:-2].split('|')
            name = s[0]
            if len(s) > 1:
                caption = s[1]
            else:
                if name in chapters:
                    caption = chapters[name]['title']
            # print name
            if name in chapters:
                repl = caption + " (see " + chapters[name]['chapter'] + ")"
            else:
                repl = "(see Chapter UNKNOWN: " + name + ")"
            # print found
            # t = t[:m.start()] + '___' + t[m.end():]
            c = c.replace(found, repl)
        return c

 
# filename = "template.docx"
# document = opendocx(filename)


imagepath = "myimages/"
document = docxwrapper(template="template.docx", imagepath=imagepath)
# document = docx.newdocument()


relationships = docx.relationshiplist()
# body = document.xpath('/w:document/w:body', namespaces=docx.nsprefixes)[0]
# body = getdocumenttext(document)


pages = open("titles.txt", 'r').read().split('\n')[0:-1]
# collect titles


countHeading1 = 0
countHeading2 = 0
countHeading3 = 0
titles = {}


# document.insertpicture('imagepy.png', 'This is a test description')

# first run
for t in pages:
    wikiname = t[2:-2]
    filename = "data/pages/" + wikiname.lower() + ".txt"

    temp = None

    countHeading1 += 1
    countHeading2 = 0
    countHeading3 = 0
    chapter = str(countHeading1)
    chapters[wikiname] = {'chapter': chapter, "title": wikiname}
    print "====" + chapter + wikiname

    try:
        temp = open(filename, 'r').read().split('\n')  #[0:-1]

    except Exception, e:
        print e
        # print filename + " not found"
        # titles[wikiname] = "leer"

    if temp:
        l = temp[0]
        h = l.replace("======", '')
        h = h[1:-1]
        # titles[pagetitle] = h

        title = h
        # print pagetitle

        for l in temp:
            if "======" in l:
                h = l.replace("======", '')
                h = h[1:-1]
                countHeading2 += 1
                countHeading3 = 0
                chapter = str(countHeading1) + "." + str(countHeading2)
                chapters[wikiname+"#"+h] = {'chapter': chapter, "title": h}

            if "=====" in l:
                h = l.replace("=====", '')
                h = h[1:-1]
                countHeading3 += 1
                chapter = str(countHeading1) + "." + str(countHeading2) + "." + str(countHeading3)
                chapters[wikiname+"#"+h] = {'chapter': chapter, "title": h}

            # if "=====" in l:
            #     h = l.replace("=====", '')
            #     h = h[1:-1]
            #     countHeading3 += 1
            #     chapter = str(countHeading1) + "." + str(countHeading2) + "." + str(countHeading3)
            #     chapters[wikiname+"#"+h] = {'chapter': chapter, "title": h}






# print chapters
import json
with open('chapters.txt', 'w') as outfile:
  json.dump(chapters, outfile, sort_keys = False, indent = 4)


# pages = pages[17:20]
# pages = pages[5:7]

import sys
# sys.exit()

# isComment = False
showComments = True
thisTable = None


# second run
for f in pages:
        filename = "data/pages/" + f[2:-2].lower() + ".txt"
        # print "====" + f

        pagetitle = f[2:-2]
        document.insert(docx.heading(pagetitle, 1))

        try:
            temp = open(filename, 'r').read().split('\n')   #[0:-1]
        except:
            print filename + " not found."
            temp = None
            pass

        if temp:
            temp.append('') # add an empty line at the end for the table end
            linecounter = -1  # counter for the table end


            for l in temp:
                linecounter += 1
                l = replaceLinks(l)
                if "======" in l:
                    h = l.replace("======", '')
                    h = h[1:-1]
                    key = f[2:-2]+"#"+h
                    h = h + "(" + chapters[key]['chapter'] + ")"
                    document.insert(docx.heading(h, 2))
                    # document.insert(docx.paragraph(h, style='EUHeading2'))

                elif "=====" in l:
                    h = l.replace("=====", '')
                    h = h[1:-1]
                    key = f[2:-2]+"#"+h
                    print key
                    h = h + "(" + chapters[key]['chapter'] + ")"
                    document.insert(docx.heading(h, 3))
                    # document.insert(paragraph(h, style='EUHeading3'))
                elif "====" in l:
                    h = l.replace("====", '')
                    h = h[1:-1]
                    document.insert(docx.heading(h, 4))
                    # document.insert(paragraph(h, style='EUHeading4'))
                elif "===" in l:
                    h = l.replace("===", '')
                    h = h[1:-1]
                    document.insert(docx.heading(h, 5))
                    # document.insert(paragraph(h, style='EUHeading5'))

                    
                elif "{{" in l[0:2]:
                    l = l.replace("{{", '')
                    l = l.replace("}}", '')
                    l = l.strip()

                    l = l.split('|')[0].strip('|')
                    l = l.split('?')

                    if l[0][0] == ":": l[0] = l[0][1:]
                    if l[0][0:4] == "http":
                        pass
                        picfilename = l[0].split('/')[-1]

                        picfile = urllib2.urlopen(l[0])
                        # print l[0] + '<------'
                        # print l[0].split('/')[-1]
                        output = open('data/media/'+picfilename,'wb')
                        output.write(picfile.read())
                        output.close() 
                        l[0] = picfilename


                    if  len(l) < 2: l.append('')                   
                    print l[0]
                    # relationships, picpara = docx.picture(relationships, l[0], l[1], document=document)
                    # document.insertpicture(l[0], l[1])

                elif l[0:1] == "|" or l[0:1] == "^":
                    if not thisTable:
                        thisTable = []
                    if l[0:1] == "|": l = l.split('|')
                    if l[0:1] == "^": l = l.split('^')
                    thisTable.append(l[1:-1])

                    # if linecounter + 1 >= len(temp):
                    #     document.insert(table(thisTable))
                    #     print thisTable
                    #     thisTable = None
                    # else:
                    if temp[linecounter+1].strip() == "":
                        # document.insert(docx.table(thisTable))
                        print thisTable
                        thisTable = None


                elif "//" in l[0:2]:
                    # isComment = not isComment
                    if showComments:
                        document.insert(docx.paragraph( [ (l, 'i')] ) )

                elif l and l[0:3] == '  *':
                    l = unicode(l, "utf-8")
                    # document.insert(docx.paragraph(''+l[4:], style='ListBullet'))
                elif l and l[0:5] == '    *':
                    document.insert(docx.paragraph('-->'+l[6:], style='Liste2'))

                elif "    " in l[0:4]:
                    document.insert(docx.paragraph("." + l, style='EUCode'))

                else:
                    c = unicode(l, "utf-8")

                    # print c
                    # ------ replace links START ----


                    # ------ replace links END ----


                    for i in titles:
                        # print "trying " + i
                        c = c.replace(i, titles[i])


                    document.insert(docx.paragraph( [ (c, '')] ) )

            # document.insert(pagebreak(type='page', orient='portrait'))


# Create our properties, contenttypes, and other support files
title    = 'Python docx demo'
subject  = 'A practical example of making docx from Python'
creator  = 'Mike MacCana'
keywords = ['python', 'Office Open XML', 'Word']

coreprops = docx.coreproperties(title=title, subject=subject, creator=creator,
                           keywords=keywords)
appprops = docx.appproperties()
contenttypes = docx.contenttypes()

websettings = docx.websettings()
wordrelationships = docx.wordrelationships(relationships)

# docx.savedocx(document, coreprops, appprops, contenttypes, websettings,
#              wordrelationships, 'test2.docx')

document.generate("test2.docx")

# print chapters

from subprocess import call
call(["open", "test2.docx"])


# unzip test.docx
# find .  | zip file.zip -@

