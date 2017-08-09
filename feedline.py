#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rapidly display fresh headlines from a TinyTinyRSS instance on the command line.

(c) 2017 Andreas Fischer <_@ndreas.de>
"""
import subprocess
import argparse
import getpass
import json
import os.path
import readchar
from ttrss import TinyTinyRSS

def get_conn():
    """
    Get connection details either from a config file, the commandline, or via user input.
    """
    conn = {}
    if os.path.isfile('pyttrss.cfg'):
        with open('pyttrss.cfg', 'r') as cfgfile:
            conn = json.load(cfgfile)

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-u', '--user', help='Username')
    parser.add_argument('-p', '--password', help='Password')
    parser.add_argument('-U', '--url', help='Server URL')
    args = parser.parse_args()
    for key, value in vars(args).iteritems():
        if value:
            conn[key] = value

    if not conn['user']:
        conn['user'] = raw_input("Enter username: ")
    if not conn['password']:
        conn['password'] = getpass.getpass()
    if not conn['url']:
        conn['url'] = raw_input("Enter server URL: ")
    return conn

if __name__ == "__main__":
    with TinyTinyRSS(get_conn()) as ttrss:
        print "Unread articles:", ttrss.getUnread()
        for article in ttrss.getHeadlines(feed_id=-3):
            outstr = u"{:>20} | {}".format(article['feed_title'][:20], article['title'])
            print outstr
            #print article['feed_title'][:20], "\t", article['title']
            char = readchar.readchar()
            if char == "o":
                subprocess.call(['xdg-open', article['link']])
            elif char == "s":
                continue
            elif char == "q":
                break
            ttrss.updateArticle(article['id'], 0, 2)
