#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.events import events
from fortunella.utils import getlogger, partial

class Plugin(object):
	def __init__(self, core, manager):
		self.core = core
		self.manager = manager
		self.logger = getlogger(self)
		self.register = self.manager.register
		self.datafile = partial(self.manager.datafile, self)
	
	def init(self, config):
		self.config = config
	
	def notice(self, user, message):
		self.logger.info('<%s> %s', user, message)
		self.core.notice(user, message)

