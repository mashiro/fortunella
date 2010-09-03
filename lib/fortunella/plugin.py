#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class Plugin(object):
	from fortunella.events import events

	def __init__(self, core, manager):
		self.core = core
		self.logger = core.logger
		self.manager = manager

