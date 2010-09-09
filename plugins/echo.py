#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.plugin import Plugin
from fortunella.events import events

class Echo(Plugin):
	def init(self, config):
		self.register(self.echo, event=events.PRIVMSG)

	def echo(self, user, channel, message):
		self.notice(channel, message)

