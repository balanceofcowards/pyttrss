#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rapidly display fresh headlines from a TinyTinyRSS instance via a GTK status
line icon.

(c) 2017 Andreas Fischer <_@ndreas.de>
"""

import gtk
from feedline import get_conn
from ttrss import TinyTinyRSS

class ArticleViewer(object):
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.set_title("Unread article list")
        self.gtklist = gtk.List()
        self.window.add(self.gtklist)
        self.gtklist.show()
        self.window.connect("destroy", self.hide)

    def show(self, articles):
        self.gtklist.clear_items(0,-1)
        items = [gtk.ListItem(article['title']) for article in articles]
        self.gtklist.append_items(items)
        self.window.show()
        print "hi"

    def hide(self):
        self.window.hide()

class FeedIcon(object):
    def __init__(self, ttrss):
        self.ttrss = ttrss
        self.viewer = ArticleViewer()
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_icon_name("mail-read")
        self.update_headlines()
        gtk.timeout_add(1000 * 60, self.update_headlines)
        self.status_icon.connect("activate", self.show_viewer)

    def update_headlines(self):
        """
        Get all unread headlines from the server.
        """
        self.headlines = self.ttrss.getHeadlines(feed_id=-4, view_mode="unread")
        count = len(self.headlines)
        if count > 0:
            self.status_icon.set_from_icon_name("mail-unread")
        else:
            self.status_icon.set_from_icon_name("mail-read")
        self.status_icon.set_tooltip_text("Unread articles: {}".format(count))
        return True

    def show_viewer(self, event):
        self.viewer.show(self.headlines)

if __name__ == "__main__":
    conn = get_conn()
    ttrss = TinyTinyRSS(conn)
    feedicon = FeedIcon(ttrss)
    gtk.main()
