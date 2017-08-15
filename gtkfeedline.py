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
        #self.window.set_geometry_hints(None, min_width=100, min_height=100, max_width=100, max_height=100)
        self.window.connect("destroy", self.hide)
        self.window.connect("key_press_event", self.on_key_pressed)

    def show(self, articles):
        treestore = gtk.TreeStore(str)
        for article in articles:
            treestore.append(None, [article['title']])
        treeview = gtk.TreeView(treestore)
        tvcolumn = gtk.TreeViewColumn('Articles: {}'.format(len(articles)))
        treeview.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        self.window.add(treeview)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.window.show_all()

    def hide(self, event):
        self.window.hide()

    def on_key_pressed(self, window, event):
        pass

class FeedIcon(object):
    def __init__(self, ttrss):
        self.ttrss = ttrss
        self.viewer = ArticleViewer()
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_icon_name("mail-read")
        self.update_headlines()
        gtk.timeout_add(1000 * 60, self.update_headlines)
        self.status_icon.connect("activate", self.toggle_viewer)

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

    def toggle_viewer(self, event):
        if self.viewer.window.get_visible():
            self.viewer.hide(event)
        else:
            self.viewer.show(self.headlines)

if __name__ == "__main__":
    conn = get_conn()
    ttrss = TinyTinyRSS(conn)
    feedicon = FeedIcon(ttrss)
    gtk.main()
