"""
    This module provides the TinyTinyRSS class as a wrapper around the
    TinyTinyRSS REST API.

    (c) 2017 Andreas Fischer
"""
import requests

class TinyTinyRSS(object):
    """ This class is a wrapper around the TinyTinyRSS REST API. """
    def __init__(self, conn):
        self.url = conn['url']
        self.session_id = None
        data = {"op": "login", "user": conn['user'], "password": conn['password']}
        data = self.rest(data)
        if 'session_id' in data['content']:
            self.session_id = data['content']['session_id']
        else:
            raise Exception("Connection error", str(data))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.session_id:
            data = {"op": "logout"}
            self.rest(data)

    def rest(self, data):
        """ Execute a single REST call to the API with JSON-encoded parameter 'data'."""
        if self.session_id:
            data["sid"] = self.session_id
        req = requests.get(self.url, json=data)
        return req.json()

    def newarticles(self):
        """ Get a list of all new articles. """
        data = {"op": "getHeadlines", "feed_id": -3}
        content = self.rest(data)['content']
        return content

    def getUnread(self):
        """ Get the number of unread articles."""
        data = {"op": "getUnread"}
        content = self.rest(data)['content']
        return content['unread']

    def markread(self, article_id):
        """ Mark a single article as read."""
        data = {"op": "updateArticle", "article_ids": article_id, "field": 2, "mode": 0}
        self.rest(data)

