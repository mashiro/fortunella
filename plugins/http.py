#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella import Plugin
from fortunella.events import events
import re

class Http(Plugin):
	def init(self, config):
		self.register(self.cmd, command='t')
		self.register(self.privmsg, event=events.PRIVMSG)
	
	def cmd(self, command, user, channel, params):
		for param in params:
			self.notice(channel, 'http://twitter.com/%s' % param)

	def privmsg(self, user, channel, message):
		self.notice(channel, message)

