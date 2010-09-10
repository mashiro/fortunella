#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fortunella.plugin import Plugin
from fortunella.events import events
from fortunella.utils import isallowed
import urllib
import urllib2
from string import Template
try:
    import json
except ImportError:
    import simplejson as json

class GoogleSearch(Plugin):
    def init(self, config):
        self.config = config or {}
        self.config.setdefault('command', 'g')
        self.config.setdefault('v', '1.0')
        self.config.setdefault('rsz', 'small')
        self.config.setdefault('hr', 'ja')
        self.config.setdefault('referer', 'http://github.com/mashiro/fortunella')

        if 'Web' in self.config:
            self.web = self.config.get('Web')  or {}
            self.web.setdefault('command', 'g')
            self.web.setdefault('template', '$titleNoFormatting $url')
            options = dict(lr=self.web.setdefault('lr', 'lang_ja'),
                           safe=self.web.setdefault('safe', 'off'))
            self.register(self.search('web', self.web, options),
                          command=self.web['command'])

        if 'Image' in self.config:
            self.image = self.config.get('Image') or {}
            self.image.setdefault('command', 'gi')
            self.image.setdefault('template', '$titleNoFormatting [${width}x${height}] $url $originalContextUrl')
            options = dict(safe=self.image.setdefault('safe', 'off'))
            self.register(self.search('images', self.image, options),
                          command=self.image['command'])

    def search(self, suffix, config, options):
        def inner(command, user, channel, params):
            if isallowed(config, channel):
                template = Template(config['template'])
            for result in self.fetch(suffix, params, **options):
                message = template.safe_substitute(result)
                self.notice(channel, message)
        return inner

    def fetch(self, suffix, params, **options):
        query = dict(q=' '.join(params).encode('utf-8'),
                     v=self.config['v'],
                     rsz=self.config['rsz'],
                     hr=self.config['hr'],
                     **options)
        headers = dict(Referer=self.config['referer'])
        url = 'http://ajax.googleapis.com/ajax/services/search/%s?%s' % (suffix, urllib.urlencode(query))
        req = urllib2.Request(url, headers=headers)
        res = urllib2.urlopen(req)
        data = res.read().decode('utf-8')
        jsondata = json.loads(data)
        return jsondata['responseData']['results']

