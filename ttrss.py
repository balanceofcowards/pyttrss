#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        self.api_level = None
        self.login(conn['user'], conn['password'])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.session_id:
            self.logout()

    def _handle_id_list(self, id_list):
        strlist = None
        if hasattr(id_list, "__iter__"):
            if len(id_list) > 0:
                strlist = ",".join([str(article) for article in id_list])
        else:
            strlist = str(id_list)
        return strlist

    def rest(self, data):
        """ Execute a single REST call to the API with JSON-encoded parameter 'data'."""
        if self.session_id:
            data["sid"] = self.session_id
        req = requests.get(self.url, json=data)
        data = req.json()
        if data['status'] == 1:
            raise Exception("Server Error -- " + data['content']['error'])
        return data

    def getApiLevel(self):
        """
        Return an abstracted integer API version level, increased with each API
        functionality change.  This is the proper way to detect host API
        functionality, instead of using getVersion.
        Whether tt-rss returns error for this method (e.g. version:1.5.7 and
        below) client should assume API level 0.
        """
        req = {"op": "getApiLevel"}
        self.api_level = self.rest(req)['content']['level']
        return self.api_level

    def getVersion(self):
        """
        Returns tt-rss version. As of, version:1.5.8 it is not recommended to
        use this to detect API functionality, please use getApiLevel instead.
        """
        req = {"op": "getVersion"}
        return self.rest(req)['content']['version']

    def login(self, user, password):
        """
        Parameters:
            * user (string)
            * password (string)
        Stores the client session ID in this.session_id
        In case it isn't immediately obvious, you have to login and get a
        session ID even if you are using single user mode. You can omit user
        and password parameters.  On version:1.6.0 and above login also returns
        current API level as an api_level integer, you can use that instead of
        calling getApiLevel after login.
        """
        req = {"op": "login", "user": user, "password": password}
        resp = self.rest(req)
        self.session_id = resp['content']['session_id']
        self.api_level = resp['content']['api_level']

    def logout(self):
        """
        Closes your login session.
        """
        req = {"op": "logout"}
        self.rest(req)

    def isLoggedIn(self):
        """
        Returns a boolean value showing whether your client (e.g. specific
        session ID) is currently logged in.
        """
        req = {"op": "isLoggedIn"}
        return self.rest(req)['content']['status']

    def getUnread(self):
        """
        Returns an integer value of currently unread articles.
        """
        req = {"op": "getUnread"}
        return self.rest(req)['content']['unread']

    def getCounters(self, output_mode="flc"):
        """
        Returns JSON-encoded counter information. Requires version:1.5.0.
            * output_mode (string, default: flc) - what kind of information to
              return (f - feeds, l - labels, c - categories, t - tags)
        """
        req = {"op": "getCounters", "output_mode": output_mode}
        return self.rest(req)['content']

    def getFeeds(self, cat_id=None, unread_only=None, limit=None, offset=None,
            include_nested=None):
        """
        Returns JSON-encoded list of feeds. The list includes category id,
        title, feed url, etc.
        Parameters:
            * cat_id (integer) - return feeds under category cat_id
            * unread_only (bool) - only return feeds which have unread articles
            * limit (integer) - limit amount of feeds returned to this value
            * offset (integer) - skip this amount of feeds first
            * include_nested (bool) - include child categories (as Feed objects
              with is_cat set) requires version:1.6.0
        Pagination:
        Limit and offset are useful if you need feedlist pagination. If you use
        them, you shouldn’t filter by unread, handle filtering in your app
        instead.
        Special category IDs are as follows:
            * 0 Uncategorized
            * -1 Special (e.g. Starred, Published, Archived, etc.)
            * -2 Labels
        Added in version:1.5.0:
            * -3 All feeds, excluding virtual feeds (e.g. Labels and such)
            * -4 All feeds, including virtual feeds
        Known bug: Prior to version:1.5.0 passing null or 0 cat_id to this
        method returns full list of feeds instead of Uncategorized feeds only.
        """
        req = {k: v for k, v in locals().iteritems() if v and k != "self"}
        req["op"] = "getFeeds"
        return self.rest(req)['content']

    def getCategories(self, unread_only=None, enable_nested=None,
            include_empty=None):
        """
        Returns JSON-encoded list of categories with unread counts.
            * unread_only (bool) - only return categories which have unread
              articles
            * enable_nested (bool) - switch to nested mode, only returns
              topmost categories requires version:1.6.0
            * include_empty (bool) - include empty categories requires
              version:1.7.6
        Nested mode in this case means that a flat list of only topmost
        categories is returned and unread counters include counters for child
        categories.
        This should be used as a starting point, to display a root list of all
        (for backwards compatibility) or topmost categories, use getFeeds to
        traverse deeper.
        """
        req = {k: v for k, v in locals().iteritems() if v and k != "self"}
        req["op"] = "getCategories"
        return self.rest(req)['content']

    def getHeadlines(self, feed_id=None, limit=None, skip=None, filter=None,
            is_cat=None, show_excerpt=None, show_content=None, view_mode=None,
            include_attachments=None, since_id=None, include_nested=None,
            order_by=None, sanitize=True, force_update=False,
            has_sandbox=False, include_header=None, search=None,
            search_mode="this_feed", match_on=None):
        """
        Returns JSON-encoded list of headlines.
        Parameters:
            * feed_id (integer) - only output articles for this feed
            * limit (integer) - limits the amount of returned articles (see
              below)
            * skip (integer) - skip this amount of feeds first
            * filter (string) - currently unused (?)
            * is_cat (bool) - requested feed_id is a category
            * show_excerpt (bool) - include article excerpt in the output
            * show_content (bool) - include full article text in the output
            * view_mode (string = all_articles, unread, adaptive, marked,
              updated)
            * include_attachments (bool) - include article attachments (e.g.
              enclosures) requires version:1.5.3
            * since_id (integer) - only return articles with id greater than
              since_id requires version:1.5.6
            * include_nested (boolean) - include articles from child categories
              requires version:1.6.0
            * order_by (string) - override default sort order requires
              version:1.7.6
            * sanitize (bool) - sanitize content or not requires version:1.8
              (default: true)
            * force_update (bool) - try to update feed before showing headlines
              requires version:1.14 (api 9) (default: false)
            * has_sandbox (bool) - indicate support for sandboxing of iframe
              elements (default: false)
            * include_header (bool) - adds status information when returning
              headlines, instead of array(articles) return value changes to
              array(header, array(articles)) (api 12)
        Limit: Maximum amount of returned headlines is capped at 200.
        These parameters might change in the future (supported since API level 2):
            * search (string) - search query (e.g. a list of keywords)
            * search_mode (string) - all_feeds, this_feed (default),
              this_cat (category containing requested feed)
            * match_on (string) - ignored
        Special feed IDs are as follows:
            -1 starred
            -2 published
            -3 fresh
            -4 all articles
            0 - archived
            IDs < -10 labels
        Sort order values:
            * date_reverse - oldest first
            * feed_dates - newest first, goes by feed date
            * (nothing) - default
        """
        req = {k: v for k, v in locals().iteritems() if v and k != "self"}
        req["op"] = "getHeadlines"
        return self.rest(req)['content']

    def updateArticle(self, article_ids, mode, field, data=None):
        """
        Update information on specified articles.
        Parameters:
            * article_ids (comma-separated list of integers) - article IDs to
              operate on
            * mode (integer) - type of operation to perform (0 - set to false,
              1 - set to true, 2 - toggle)
            * field (integer) - field to operate on (0 - starred, 1 -
              published, 2 - unread, 3 - article note since api level 1)
            * data (string) - optional data parameter when setting note field
              (since api level 1)
        E.g. to set unread status of articles X and Y to false use the following:
        updateArticle([X, Y], 0, 2)
        Returns the number of articles updated by the query.
        """
        req = {"op": "updateArticle", "mode": mode, "field": field,
                "data": data}
        req["article_ids"] = self._handle_id_list(article_ids)
        return self.rest(req)['content']['updated'] if req["article_ids"] else 0

    def getArticle(self, article_id):
        """
        Requests JSON-encoded article object with specific ID.
            * article_id (integer) - article ID to return as of 15.10.2010 git
            or version:1.5.0 supports comma-separated list of IDs
        Since version:1.4.3 also returns article attachments.
        """
        req = {"op": "getArticle"}
        req["article_id"] = self._handle_id_list(article_id)
        return self.rest(req)['content'] if req["article_id"] else None

    def getConfig(self):
        """
        Returns tt-rss configuration parameters:
        {"icons_dir":"icons","icons_url":"icons","daemon_is_running":true,"num_feeds":71}
            * icons_dir - path to icons on the server filesystem
            * icons_url - path to icons when requesting them over http
            * daemon_is_running - whether update daemon is running
            * num_feeds - amount of subscribed feeds (this can be used to
              refresh feedlist when this amount changes)
        """
        req = {"op": "getConfig"}
        return self.rest(req)['content']

    def updateFeed(self, feed_id):
        """
        Tries to update specified feed. This operation is not performed in the
        background, so it might take considerable time and, potentially, be
        aborted by the HTTP server.
            * feed_id (integer) - ID of feed to update
        """
        req = {"op": "getConfig", "feed_id": feed_id}
        self.rest(req)

    def getPref(self, pref_name):
        """
        Returns preference value of specified key.
            * pref_name (string) - preference key to return value of
        """
        req = {"op": "getConfig", "pref_name": pref_name}
        return self.rest(req)['content']['value']

    def catchupFeed(self, feed_id, is_cat):
        """
        Tries to catchup (e.g. mark as read) specified feed.
        Parameters:
            * feed_id (integer) - ID of feed to update
            * is_cat (boolean) - true if the specified feed_id is a category
        """
        req = {"op": "catchupFeed", "feed_id": feed_id, "is_cat": is_cat}
        self.rest(req)

    def getLabels(self, article_id=None):
        """
        Returns list of configured labels, as an array of label objects:
        {"id":2,"caption":"Debian","fg_color":"#e14a00","bg_color":"#ffffff","checked":false},
        Parameters:
            * article_id (int) - set “checked” to true if specified article id
            has returned label.
        """
        req = {"op": "getLabels"}
        if article_id:
            req["article_id"] = article_id
        return self.rest(req)['content']

    def setArticleLabel(self, article_ids, label_id, assign):
        """
        Assigns article_ids to specified label.
        Parameters:
            * article_ids - comma-separated list of article ids
            * label_id (int) - label id, as returned in getLabels
            * assign (boolean) - assign or remove label
        """
        req = {"op": "setArticleLabel", "label_id": label_id, "assign": assign}
        article_string = self._handle_id_list(article_ids)
        if article_string:
            req["article_ids"] = article_string
            self.rest(req)

    def shareToPublished(self, title, url, content):
        """
        Creates an article with specified data in the Published feed.
        Parameters:
            * title - Article title (string)
            * url - Article URL (string)
            * content - Article content (string)
        """
        req = {"op": "shareToPublished", "title": title, "url": url,
               "content": content}
        self.rest(req)

    def subscribeToFeed(self, feed_url, login, password, category_id = 0):
        """
        Subscribes to specified feed, returns a status code. See
        subscribe_to_feed() in functions.php for details.
        Parameters:
            * feed_url - Feed URL (string)
            * login, password - Self explanatory (string)
            * category_id - Category id to place feed into (defaults to 0,
              Uncategorized) (int)
        """
        req = {"op": "subscribeToFeed", "feed_url": feed_url,
               "category_id": category_id, "login": login,
               "password": password}
        self.rest(req)

    def unsubscribeFeed(self, feed_id):
        """
        Unsubscribes specified feed.
        Parameters:
            * feed_id - Feed id to unsubscribe from
        """
        req = {"op": "unsubscribeFeed", "feed_id": feed_id}
        self.rest(req)

    def getFeedTree(self, include_empty):
        """
        Returns full tree of categories and feeds.
        Parameters:
            * include_empty (bool) - include empty categories
        Note: counters for most feeds are not returned with this call for
        performance reasons.
        """
        req = {"op": "getFeedTree", "include_empty": include_empty}
        return self.rest(req)['content']
