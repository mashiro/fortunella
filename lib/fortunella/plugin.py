#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.events import events
import logging

class Plugin(object):
	def __init__(self, core, manager):
		self.core = core
		self.manager = manager
		self.logger = self._getlogger(self)
		self.register = self.manager.register
	
	def notice(self, user, message):
		self.logger.info('<%s> %s', user, message)
		self.core.notice(user, message)

	@classmethod
	def _getlogger(cls, instance):
		klass = instance.__class__
		name = '%s.%s' % (klass.__module__.replace('/', '.'), klass.__name__)
		return logging.getLogger('fortunella.%s' % name)

