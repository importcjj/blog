#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'importcjj'
SITENAME = u'Signal'
# SITEURL = 'http://www.importcjj.com'

THEME = 'theme/yake'
PATH = 'content'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Side bar items
GITHUB_URL = 'https://github.com/importcjj'

# Blogroll
LINKS = (('Slade', 'http://chihiro.moe'),
         ('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'))

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10
DISQUS_SITENAME = 'importcjj'
BUILD_STATUS_URL = 'https://travis-ci.org/importcjj/importcjj.github.io.svg?branch=master'

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True
