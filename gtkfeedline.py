#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Rapidly display fresh headlines from a TinyTinyRSS instance via a GTK status
line icon.

(c) 2017 Andreas Fischer <_@ndreas.de>
"""

import gtk
import webbrowser
from feedline import get_conn
from ttrss import TinyTinyRSS

class ArticleViewer(object):
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_DIALOG)
        self.window.set_title("Unread article list")
        #self.window.set_geometry_hints(None, min_width=100, min_height=100, max_width=100, max_height=100)
        self.window.connect("destroy", self.hide)
        #self.window.connect("key_press_event", self.on_key_pressed)
        self.read = []

    def show(self, articles):
        treestore = gtk.TreeStore(str, str, str, int)
        for article in articles:
            entry = [article['title'], article['link'], article['id'], 700]
            treestore.append(None, entry)
        treeview = gtk.TreeView(treestore)
        tvcolumn = gtk.TreeViewColumn('Articles: {}'.format(len(articles)))
        treeview.append_column(tvcolumn)
        cell = gtk.CellRendererText()
        tvcolumn.pack_start(cell, True)
        tvcolumn.add_attribute(cell, 'text', 0)
        tvcolumn.add_attribute(cell, 'weight', 3)
        self.window.add(treeview)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        treeview.connect("row-activated", self.open_article, treestore)
        treeview.connect("cursor-changed", self.skip_article, treestore)
        self.window.show_all()

    def hide(self, event):
        self.window.hide()
        self.on_hide()

    def on_hide(self):
        pass

    def on_key_pressed(self, window, event):
        key = event.keyval
        if key == "Return":
            pass
        elif key == "space":
            pass

    def open_article(self, treeview, path, view_column, treestore):
        treeiter = treestore.get_iter(path)
        url = treestore.get_value(treeiter, 1)
        webbrowser.open(url)
        a = path[0]
        treeview.set_cursor((a+1))
        treestore.set_value(treeiter, 3, 400)
        artid = treestore.get_value(treeiter, 2)
        if artid not in self.read:
            self.read.append(artid)

    def skip_article(self, treeview, treestore):
        path, _ = treeview.get_cursor()
        treeiter = treestore.get_iter(path)
        treestore.set_value(treeiter, 3, 400)
        artid = treestore.get_value(treeiter, 2)
        if artid not in self.read:
            self.read.append(artid)

class FeedIcon(object):
    def __init__(self, ttrss):
        self.ttrss = ttrss
        self.menu = gtk.Menu()
        quitter = gtk.ImageMenuItem(gtk.STOCK_QUIT)
        quitter.set_always_show_image(True)
        self.menu.append(quitter)
        quitter.show()
        quitter.connect("activate", gtk.main_quit)
        self.viewer = ArticleViewer()
        self.viewer.on_hide = self.update_articles
        self.status_icon = gtk.StatusIcon()
        self.status_icon.set_from_icon_name("mail-read")
        self.update_headlines()
        self.to = gtk.timeout_add(1000 * 60, self.update_headlines)
        self.status_icon.connect("activate", self.toggle_viewer)
        self.status_icon.connect("popup-menu", self.show_menu)

    def update_articles(self):
        ids = self.viewer.read
        self.ttrss.updateArticle(ids, 0, 2)
        self.viewer.read = []
        gtk.timeout_remove(self.to)
        self.update_headlines()
        self.to = gtk.timeout_add(1000 * 60, self.update_headlines)

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

    def show_menu(self, status_icon, button, activate_time):
        self.menu.popup(None, None, None, button, activate_time)

if __name__ == "__main__":
    conn = get_conn()
    ttrss = TinyTinyRSS(conn)
    feedicon = FeedIcon(ttrss)
    gtk.main()
