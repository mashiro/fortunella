#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella import Plugin
from fortunella.events import events
import urllib
import urllib2
from string import Template
try:
	import json
except ImportError:
	import simplejson as json

class GoogleImageSearch(Plugin):
	def init(self, config):
		self.config = config or {}
		self.config.setdefault('prefix', 'gi')
		self.config.setdefault('template', '$titleNoFormatting [${width}x${height}] $url $originalContextUrl')
		self.config.setdefault('safe', 'off')

		self.config.setdefault('v', '1.0')
		self.config.setdefault('rsz', 'small')
		self.config.setdefault('hr', 'ja')
		self.config.setdefault('referer', 'http://github.com/mashiro/fortunella')
		self.register(self.search, command=self.config['prefix'])
	
	def makequery(self, params, **kwargs):
		d = dict(q=' '.join(params).encode('utf-8'), v=self.config['v'], rsz=self.config['rsz'], hr=self.config['hr'], **kwargs)
		return urllib.urlencode(d)

	def fetch(self, suffix, query):
		headers = dict(Referer=self.config['referer'])
		url = 'http://ajax.googleapis.com/ajax/services/search/%s?%s' % (suffix, query)
		req = urllib2.Request(url, headers=headers)
		res = urllib2.urlopen(req)
		return res.read().decode('utf-8')

	def search(self, command, user, channel, params):
		template = Template(self.config['template'])
		query = self.makequery(params, safe=self.config['safe'])
		data = self.fetch('images', query)
		jsondata = json.loads(data)
		results = jsondata['responseData']['results']
		for result in results:
			message = template.safe_substitute(result)
			self.notice(channel, message)

