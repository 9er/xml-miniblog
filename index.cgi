#!/usr/bin/python
# -*- coding: utf-8 -*-

from xml.dom.minidom import parse
from os import path, listdir
from datetime import datetime
from re import sub
import cgi



def getText(element):
    texts = []
    for node in element.childNodes:
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
            texts.append(node.data)
    return ''.join(texts).encode("utf-8")

def getNodeText(parent, tagname):
    element = parent.getElementsByTagName(tagname)[0]
    return getText(element)

def nicedate(timestamp):
    date = datetime.fromtimestamp(int(timestamp))
    monthname = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"][date.month - 1]
    return "".join([str(date.day), ". ", monthname, " ", str(date.year)])

def getURL(date, title):
    return sub(r"\W+", "-", date + " " + title)



# folder name for blogposts
ITEM_PATH = "items"

# send http header
print "Content-Type: text/html"
print


################
# PARSE CONFIG #
################
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
    footer = getNodeText(settings, "footer")
except:
    footer = ""



#########################
# PARSE HTTP-GET PARAMS #
#########################
params = cgi.FieldStorage()
try:
    page = int(params.getvalue(pagekey)) -1
except:
    page = 0
try:
    post = params.getvalue(postkey)
except:
    post = None


items = []
displayed_items = []
files = []

#################################
# SEARCH + PARSE XML BLOG POSTS #
#################################
try:
    dirlist = listdir(ITEM_PATH)
except:
    dirlist = []
for item in dirlist:
    if item[-4:] == ".xml" and not path.isdir(path.join(ITEM_PATH, item)):
        files.append(item)
files.sort(reverse=True)
entries_total = len(files)
for xmlfile in files:
    items.append(parse(path.join(ITEM_PATH, xmlfile)))


# display single item
if post:
    for xmlfile in files:
        dom = parse(path.join(ITEM_PATH, xmlfile))
        if getURL(nicedate(getNodeText(dom, "timestamp")), getNodeText(dom, "title")) == post:
            displayed_items.append(dom)
# 10 blog posts per page
else:
    displayed_items = items[page*10:page*10 + 9]






##############
# BUILD HTML #
##############
print("""<!DOCTYPE html>
<html lang="de">

<head>
    <title>""" + title + """</title>
    <meta charset="utf-8" />
    <link href="favicon.ico" rel="shortcut icon" />
    <link rel="stylesheet" href="style.css" type="text/css" />
    <link rel="alternate" type="application/atom+xml" title="Newsfeed" href="feed.cgi" />
</head>

<body>
<div id="container">

<a href="." class="main_title"><div id="header">
    <h1>""" + title + """</h1>
</div></a>

<div id="main">
<div id="blogposts">
""")

# next page link (to newer posts)
if page > 0 and not post:
    print("<p class=\"nextpage\"><a href=\"?" + pagekey + "=" + str(page) + "\">&lt;&lt; " + label_nextposts + "</a></p>")

# display blog posts
for item in displayed_items:
    print("<div class=\"item\">")
    date = nicedate(getNodeText(item, "timestamp"))
    url = postkey + "=" + getURL(date, getNodeText(item, "title"))
    print("    <a class=\"itemtitle\" href=\"?" + url + "\"><div class=\"itemtitle\"><span class=\"date\">" + date + "</span><h2>" + getNodeText(item, "title") + "</h2></div></a>")
    print(getNodeText(item, "content"))
    print("</div>")

# previous page link (older posts)
if entries_total > (page*10 + 9) and not post:
    print("<p class=\"nextpage\"><a href=\"?" + pagekey + "=" + str(page + 2) + "\">&lt;&lt; " + label_prevposts + "</a></p>")

print("""
</div>

<div id="sidebar">
    <h4>Newsfeed</h4>
    <div id="icons"><a href="feed.cgi"><img src="feed.svg" alt="Newsfeed" /></a></div>
    <h4>""" + label_entries + " (" + str(entries_total) + """)</h4>
    <ul class="sidebar">""")

# all posts titles in sidebar
for item in items:
    date = nicedate(getNodeText(item, "timestamp"))
    url = postkey + "=" + getURL(date, getNodeText(item, "title"))
    print("        <li><a href=\"?" + url + "\"><p class=\"listdate\">" + getNodeText(item, "date") + "</p><p class=\"listtitle\">" + getNodeText(item, "title") + "</p></a></li>")

print("""
    </ul>
</div>
</div>

<div id="footer">
   """ + footer + """
</div>

</div>
</body>
</html>""")
