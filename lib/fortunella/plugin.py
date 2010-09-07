#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.events import events
from fortunella.utils import getlogger

class Plugin(object):
	def __init__(self, core, manager):
		self.core = core
		self.manager = manager
		self.logger = getlogger(self)
		self.register = self.manager.register
	
	def notice(self, user, message):
		self.logger.info('<%s> %s', user, message)
		self.core.notice(user, message)

