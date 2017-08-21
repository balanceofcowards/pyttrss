# pyttrss
Python interface and utilities for accessing a TinyTinyRSS instance.

The `ttrss.py` file provides an object-oriented interface to the [TinyTinyRSS](http://tt-rss.org/) [REST API](https://tt-rss.org/wiki/ApiReference).

Two example scripts are provided:
  * `feedline.py` is a console utility, displaying all unread articles line by line and either skipping them (press `Space`) or opening them in a webbrowser (press `o`)
  * `gtkfeedline.py` provides similar functionality, creating a statusicon which gives access to the list of unread articles
  
Bug reports and pull requests are very welcome.
