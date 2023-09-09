from html import escape
from urllib import request, parse
from random import choices

import json
import os


BASE_URL = "https://api.pinboard.in/v1/posts/all"
TAG = "to-read"
COUNT = 3
TOKEN = os.environ["PINBOARD_API_TOKEN"]


def app(environ, start_response):
    bookmarks = retrieve(TAG, COUNT)
    start_response("200 OK", [("Content-Type", "text/html")])
    for html in render(bookmarks):
        yield html.encode("utf-8")


def render(bookmarks):
    yield """
<!DOCTYPE html>
<html lang="en">
<meta charset="utf-8">
<title>Bookmarks</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<h1>Bookmarks</h1>
<ul>
    """.strip()
    for bookmark in bookmarks:
        html = '<a href="%s">%s</a>' % (escape(bookmark["href"], quote=True),
                escape(bookmark["description"]))

        desc = bookmark["extended"]
        if desc != "":
            html = "%s\n<p>%s</p>" % (html, escape(desc))

        yield "<li>%s</li>" % html
    yield "</ul>"


def retrieve(tag, count):
    url = "%s?%s" % (BASE_URL, parse.urlencode({
        "tag": tag,
        "format": "json",
        "auth_token": TOKEN
    }))
    res = request.urlopen(url)
    bookmarks = json.load(res)
    return choices(bookmarks, k=count)
