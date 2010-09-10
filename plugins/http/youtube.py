#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fortunella.plugins.http import Handler
import urllib
import re
import locale
from string import Template
try:
    import xml.etree.ElementTree as etree
except ImportError:
    import elementtree.ElementTree as etree

class YouTube(Handler):
    def init(self, config):
        self.config = config or {}
        self.template = self.config.get('template', '[YouTube] $title')
        self.re_youtube = re.compile(r'(youtube\.com/watch\?.*?v=|youtu\.be\/)([\w-]+)', re.IGNORECASE)
        self.atomns = '{http://www.w3.org/2005/Atom}'

    def process(self, url):
        for match in self.re_youtube.finditer(url):
            video_id = match.group(2)
            entry = self.getvideoinfo(video_id)
            author = entry.find(self.atomns+'author')

            d = dict(id=entry.findtext(self.atomns+'id'),
                     published=entry.findtext(self.atomns+'published'),
                     updated=entry.findtext(self.atomns+'updated'),
                     title=entry.findtext(self.atomns+'title'),
                     content=entry.findtext(self.atomns+'content'),
                     author_name=author.findtext(self.atomns+'name'),
                     author_uri=author.findtext(self.atomns+'uri'))

            return Template(self.template).safe_substitute(d)
        return None

    @classmethod
    def getvideoinfo(cls, video_id):
        f = urllib.urlopen('http://gdata.youtube.com/feeds/api/videos/%s' % video_id)
        return etree.parse(f)

