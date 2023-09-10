from html import escape
from urllib import request, parse
from random import choices

import json
import os


BASE_URL = "https://api.pinboard.in/v1/posts/all"
TAG = "to-read"
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
<ul>
    """.strip()
    for bookmark in retrieve(TAG, COUNT):
        html = '<a href="%s">%s</a>' % (escape(bookmark["href"], quote=True),
                escape(bookmark["description"]))

        desc = bookmark["extended"]
        if desc != "":
            html = "%s\n<p>%s</p>" % (html, escape(desc))

        yield "<li>%s</li>" % html
    yield "</ul>"


def retrieve(tag, count):
    global BOOKMARKS
    global CACHE_HITS
    if CACHE_HITS == THRESHOLD:
        url = "%s?%s" % (BASE_URL, parse.urlencode({
            "tag": tag,
            "format": "json",
            "auth_token": TOKEN
        }))
        res = request.urlopen(url)
        BOOKMARKS = json.load(res)
        CACHE_HITS = 0
    else:
        CACHE_HITS += 1

    return choices(BOOKMARKS, k=count)
