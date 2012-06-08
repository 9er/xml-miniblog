#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
from os import path, listdir
from urllib import quote_plus
from datetime import datetime
from re import sub

def getText(element):
    rc = []
    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
            rc.append(node.data)
    return ''.join(rc).encode("utf-8")

def getNodeText(parent, tagname):
    element = parent.getElementsByTagName(tagname)[0]
    return getText(element)

def isotime(timestamp):
    return datetime.utcfromtimestamp(int(timestamp)).isoformat() + "Z"

def nicedate(timestamp):
    return datetime.fromtimestamp(int(timestamp)).strftime("%d.%m.%Y")

def getURL(date, title):
    return sub(r"\W+", "-", date + " " + title)

ITEM_PATH = "items"

print "Content-Type: text/html"
print

settings = parse("settings.xml")
try:
    lang = settings.getElementsByTagName("language")[0]
    try:
        pagekey = getNodeText(lang, "pagekey")
    except IndexError:
        pagekey = "page"
    try:
        postkey = getNodeText(lang, "postkey")
    except IndexError:
        postkey = "post"
    try:
        label_nextposts = getNodeText(lang, "label_nextposts")
    except IndexError:
        label_nextposts = "more recent posts"
    try:
        label_prevposts = getNodeText(lang, "label_prevposts")
    except IndexError:
        label_prevposts = "older posts"
    try:
        label_entries = getNodeText(lang, "label_entries")
    except IndexError:
        label_entries = "entries"
except Exception, e:
    print(str(e))
try:
    title = getNodeText(settings, "title")
except:
    title = "[no title set]"
try:
    link = getNodeText(settings, "link")
except:
    link = ""
try:
    feed_items = int(getNodeText(settings, "title"))
except:
    feed_items = 50

items = []
files = []
dirlist = listdir(ITEM_PATH)
for item in dirlist:
    if item[-4:] == ".xml" and not path.isdir(path.join(ITEM_PATH, item)):
        files.append(item)
files.sort(reverse=True)
entries_total = len(files)

for xmlfile in files[:feed_items]:
    items.append(parse(path.join(ITEM_PATH, xmlfile)))

last_update = int(getNodeText(items[0], "timestamp"))


print("""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>""" + title + """</title>
    <updated>""" + isotime(last_update) + """</updated>
    <icon>""" + link + """favicon.ico</icon>
""")

for item in items:
    print("    <entry>")
    date = nicedate(getNodeText(item, "timestamp"))
    url = link + "?" + postkey + "=" + getURL(date, getNodeText(item, "title"))
    print("        <title>" + getNodeText(item, "title") + "</title>")
    print("        <link rel=\"alternate\" type=\"text/html\" href=\"" + url + "\" />")
    print("        <updated>" + isotime(getNodeText(item, "timestamp")) + "</updated>")
    print("        <published>" + isotime(getNodeText(item, "timestamp")) + "</published>")
    print("        <content type=\"html\" xml:base=\"" + url + "\"><![CDATA[" + getNodeText(item, "content") + "]]></content>")
    print("    </entry>")

print("""
</feed>""")
