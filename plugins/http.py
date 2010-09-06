#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella import Plugin
from fortunella.events import events
import re
import urllib2

class Http(Plugin):
	def init(self, config):
		self.re_url = re.compile(r'https?://[^ ]+', re.IGNORECASE | re.DOTALL)
		self.register(self.cmd, command='t')
		self.register(self.privmsg, event=events.PRIVMSG)
	
	def cmd(self, command, user, channel, params):
		for param in params:
			self.notice(channel, 'http://twitter.com/%s' % param)

	def privmsg(self, user, channel, message):
#		import time
#		time.sleep(5)
		self.notice(channel, message)

