#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class Enum(object):
	def __init__(self, *names):
		self.names = list(names)
		for index, name in enumerate(names):
			setattr(self, name, index)
	
	def name(self, index):
		return self.names[index]

events = Enum(
	'PLUGIN_LOAD_COMPLETE',

	'CONNECTIN_MADE',
	'CONNECTIN_LOST',
	'SIGNED_ON',

	'JOIN',
	'LEFT',
	'QUIT',
	'MODE',
	'TALK',
	'PRIVMSG',
	'NOTICE',
	'NICK',
	'KICK',
	'TOPIC',

	'COMMAND')

