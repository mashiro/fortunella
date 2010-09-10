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

class NicoVideo(Handler):
    def init(self, config):
        self.config = config or {}
        self.template = self.config.get('template',
                u'[NicoVideo] $title ($length) [再生: $view_counter コメ: $comment_num マイ: $mylist_counter]')
        self.re_nicovideo = re.compile(r'(nicovideo\.jp/watch|nico\.ms)/([a-z]{2}\d+)', re.IGNORECASE)

    def process(self, url):
        for match in self.re_nicovideo.finditer(url):
            video_id = match.group(2)
            thumb = self.getthumbinfo(video_id).find('//thumb')

            d = dict(title=thumb.findtext('title'),
                     description=thumb.findtext('description'),
                     thumbnail_url=thumb.findtext('thumbnail_url'),
                     first_retrieve=thumb.findtext('first_retrieve'),
                     length=thumb.findtext('length'),
                     view_counter=locale.format('%d', int(thumb.findtext('view_counter')), grouping=True),
                     comment_num=locale.format('%d', int(thumb.findtext('comment_num')), grouping=True),
                     mylist_counter=locale.format('%d', int(thumb.findtext('mylist_counter')), grouping=True),
                     last_res_body=thumb.findtext('last_res_body'),
                     watch_url=thumb.findtext('watch_url'),
                     thumb_type=thumb.findtext('thumb_type'),
                     user_id=thumb.findtext('user_id'))

            return Template(self.template).safe_substitute(d)
        return None

    @classmethod
    def getthumbinfo(cls, video_id):
        f = urllib.urlopen('http://ext.nicovideo.jp/api/getthumbinfo/%s' % video_id)
        return etree.parse(f)

