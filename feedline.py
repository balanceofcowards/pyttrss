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

    # Preference: Commandline > Configfile > User input
    conn['user'] = args.user or conn['user'] or raw_input("Enter username: ")
    conn['password'] = args.password or conn['password'] or getpass.getpass()
    conn['url'] = args.url or conn['url'] or raw_input("Enter server URL: ")
    return conn

if __name__ == "__main__":
    with TinyTinyRSS(get_conn()) as ttrss:
        print "Unread articles:", ttrss.getUnread()
        read_art_ids = []
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
            read_art_ids.append(article['id'])
        ttrss.updateArticle(read_art_ids, 0, 2)
