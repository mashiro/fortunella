#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class Enum(object):
	def __init__(self, *names):
		for i, name in enumerate(names):
			setattr(self, name, i)

events = Enum(
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

