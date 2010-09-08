#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.plugin import Plugin
from fortunella.events import events
from fortunella.utils import getlogger, ClassLoader
from twisted.internet import threads, reactor, defer
import sys
import re
import imp

class PluginManager(object):
	def __init__(self, core):
		self.logger = getlogger(self)
		self.core = core
		self.callbackmap = {}
		self.plugins = []
		self.plugin_module_name = 'fortunella.plugins'
		self.class_loader = ClassLoader(logger=self.logger, base=Plugin, callback=self._plugin_loaded)
		sys.modules[self.plugin_module_name] = imp.new_module(self.plugin_module_name)
	
	def _plugin_loaded(self, module, klass):
		name = klass.__name__
		if name in self.core.config.plugins:
			config = self.core.config.plugins[name]
			if not 'disabled' in config:
				plugin = klass(self.core, self)
				plugin.init(self.core.config.plugins[name])
				self.plugins.append(plugin)
				self._setmodule(module)
				return True
		return False

	def _setmodule(self, module):
		basename = '.'.join(re.split('[\./]', module.__name__)[1:])
		name = '%s.%s' % (self.plugin_module_name, basename)
		sys.modules[name] = module

	def load_plugins(self, path):
		self.callbackmap = {}
		self.plugins = []
		self.class_loader.loads(path)
	
	def reload_plugins(self):
		self.class_loader.reload()

	def register(self, func, event=None, command=None):
		if command:
			event = events.COMMAND
		callbacks = self.callbackmap.setdefault(event, [])
		callbacks.append((func, command))
		self.logger.debug('registering %s for event %s', func, events.name(event))
		return self

	def push(self, event, *args, **kwargs):
		callbacks = self.callbackmap.get(event)
		if callbacks is None:
			return

		if event == events.COMMAND:
			command = kwargs['command']
			functions = [c[0] for c in callbacks if command == c[1]]
		else:
			functions = [c[0] for c in callbacks]

		for func in functions:
			deferred = threads.deferToThread(lambda: func(*args, **kwargs))
			deferred.addErrback(self._failed)
	
	def _failed(self, failure):
		self.logger.error(failure)

