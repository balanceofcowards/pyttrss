import readchar
import subprocess
from ttrss import TinyTinyRSS

CONN = {
        "url": None,
        "user": None,
        "password": None
        }

if __name__ == "__main__":
    with TinyTinyRSS(CONN) as ttrss:
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
