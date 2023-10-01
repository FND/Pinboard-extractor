from html import escape
from urllib import request, parse
from random import choices
from collections import defaultdict

import json
import os


BASE_URL = "https://api.pinboard.in/v1/posts/all"
TAGS = ["next", "to-read", "to-watch"]
COUNT = 3
TOKEN = os.environ["PINBOARD_API_TOKEN"]

BOOKMARKS = None
THRESHOLD = 5
CACHE_HITS = THRESHOLD


def app(environ, start_response):
    uri = environ.get("PATH_INFO", "")
    if uri == "/health":
        start_response("200 OK", [("Content-Type", "text/plain")])
        return []

    if uri != "/":
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return []

    start_response("200 OK", [("Content-Type", "text/html")])
    for html in render():
        yield html.encode("utf-8")


def render():
    yield """
<!DOCTYPE html>
<html lang="en">
<meta charset="utf-8">
<title>Bookmarks</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<h1>Bookmarks</h1>
    """.strip()

    bookmarks, selection = retrieve(TAGS, COUNT)
    yield from renderBlock("Random Selection", selection)

    for tag in TAGS:
        yield from renderBlock(tag, bookmarks[tag])


def renderBlock(title, bookmarks):
    yield """
<h2>%s</h2>
<ul>
    """.strip() % title
    for bookmark in bookmarks:
        yield "<li>%s</li>" % renderBookmark(bookmark)
    yield "</ul>"


def renderBookmark(bookmark):
    html = '<a href="%s">%s</a>\n' % (escape(bookmark["href"], quote=True),
            escape(bookmark["description"]))

    desc = bookmark["extended"]
    if desc != "":
        html += "<p>%s</p>\n" % escape(desc)

    return html + ", ".join("<i>%s</i>" % tag for tag in bookmark["tags"])


def retrieve(tags, count):
    global BOOKMARKS
    global CACHE_HITS
    if CACHE_HITS == THRESHOLD:
        url = "%s?%s" % (BASE_URL, parse.urlencode({
            "tags": " ".join(tags),
            "format": "json",
            "auth_token": TOKEN
        }))
        res = request.urlopen(url)
        entries = json.load(res)
        BOOKMARKS = defaultdict(list)
        for bookmark in entries:
            bookmark["tags"] = bookmark["tags"].split(" ")
            for tag in bookmark["tags"]:
                if tag in tags:
                    BOOKMARKS[tag].append(bookmark)
                    BOOKMARKS["_all"].append(bookmark) # XXX: inelegant
        CACHE_HITS = 0
    else:
        CACHE_HITS += 1
    return BOOKMARKS, choices(BOOKMARKS["_all"], k=count)


if __name__ == "__main__": # for debugging purposes only
    for html in render():
        print(html)
