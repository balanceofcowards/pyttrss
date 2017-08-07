import readchar
import subprocess
import argparse
import getpass
import json
import os.path
from ttrss import TinyTinyRSS

if __name__ == "__main__":
    conn = {}
    if os.path.isfile('pyttrss.cfg'):
        with open('pyttrss.cfg', 'r') as cfgfile:
            conn = json.load(cfgfile)

    parser = argparse.ArgumentParser(description='Show a list of recent articles.')
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

    with TinyTinyRSS(conn) as ttrss:
        print "Unread articles:", ttrss.getUnread()
        for article in ttrss.newarticles():
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
            ttrss.markread(article['id'])
