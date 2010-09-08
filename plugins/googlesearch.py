#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella import Plugin
from fortunella.events import events
import urllib
import urllib2
try:
	import json
except ImportError:
	import simplejson as json

class GoogleSearch(Plugin):
	def init(self, config):
		self.config = config or {}
		self.prefix = self.config.get('prefix', 'g')
		self.version = self.config.get('version', '1.0')
		self.hr = self.config.get('hr', 'ja')
		self.lr = self.config.get('lr', 'lang_ja')
		self.safe = self.config.get('safe', 'off')
		self.referer = self.config.get('referer', 'http://github.com/mashiro/fortunella')
		self.register(self.search, command=self.prefix)

	def search(self, command, user, channel, params):
		query = dict(q=' '.join(params), v=self.version, hr=self.hr, lr=self.lr, safe=self.safe)
		headers = dict(Referer=self.referer)

		url = 'http://ajax.googleapis.com/ajax/services/search/web?%s' % urllib.urlencode(query)
		req = urllib2.Request(url, headers=headers)
		res = urllib2.urlopen(req)
		data = res.read().decode('utf-8')

		jsondata = json.loads(data)
		results = jsondata['responseData']['results']
		for result in results:
			message = '%s %s' % (result['titleNoFormatting'], result['url'])
			self.notice(channel, message)

