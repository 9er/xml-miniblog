#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
from os import path, listdir, environ
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
    date = datetime.fromtimestamp(int(timestamp))
    monthname = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"][date.month - 1]
    return "".join([str(date.day), ". ", monthname, " ", str(date.year)])

def getURL(date, title):
    return sub(r"\W+", "-", date + " " + title)

ITEM_PATH = "items"

print "Content-Type: application/atom+xml"
print

uri = "".join(environ["HTTP_HOST"], environ["REQUEST_URI"])
"/".join(uri.split("/")[:-1]) + "/"

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
    feed_items = int(getNodeText(settings, "title"))
except:
    feed_items = 50

items = []
files = []
try:
    dirlist = listdir(ITEM_PATH)
except OSError:
    dirlist = []
for item in dirlist:
    if item[-4:] == ".xml" and not path.isdir(path.join(ITEM_PATH, item)):
        files.append(item)
files.sort(reverse=True)
entries_total = len(files)

for xmlfile in files[:feed_items]:
    items.append(parse(path.join(ITEM_PATH, xmlfile)))

try:
    last_update = int(getNodeText(items[0], "timestamp"))
except IndexError:
    last_update = 0

print("""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>""" + title + """</title>
    <updated>""" + isotime(last_update) + """</updated>
    <icon>""" + uri + """favicon.ico</icon>
""")

for item in items:
    print("    <entry>")
    date = nicedate(getNodeText(item, "timestamp"))
    pageurl = uri + "index.cgi?" + postkey + "=" + getURL(date, getNodeText(item, "title"))
    feedurl = uri + "feed.cgi"
    print("        <title>" + getNodeText(item, "title") + "</title>")
    print("        <link rel=\"self\" type=\"application/atom+xml\" href=\"" + feedurl + "\" />")
    print("        <link rel=\"alternate\" type=\"text/html\" href=\"" + pageurl + "\" />")
    print("        <updated>" + isotime(getNodeText(item, "timestamp")) + "</updated>")
    print("        <published>" + isotime(getNodeText(item, "timestamp")) + "</published>")
    print("        <content type=\"html\" xml:base=\"" + pageurl + "\"><![CDATA[" + getNodeText(item, "content") + "]]></content>")
    print("    </entry>")

print("""
</feed>""")
