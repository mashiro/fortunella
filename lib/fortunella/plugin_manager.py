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
			plugin = klass(self.core, self)
			plugin.init(config)
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

		if hasattr(func, 'im_self'):
			instance = func.im_self
		else:
			instance

		callbacks = self.callbackmap.setdefault(event, [])
		callbacks.append(dict(instance=instance, func=func, command=command))
		self.logger.debug('registering %s for event %s', func, events.name(event))
		return self

	def push(self, event, *args, **kwargs):
		callbacks = self.callbackmap.get(event)
		if callbacks is None:
			return
		
		alloweds = []
		for callback in callbacks:
			instance = callback['instance']
			channel = kwargs.get('channel')
			if instance and channel:
				klass = instance.__class__
				config = self.core.config.plugins[klass.__name__]
				enabled = config.get('enabled')
				disabled = config.get('disabled')

				def ismatch(patterns, s):
					for pattern in patterns:
						if re.search(pattern, s):
							return True
					return False

				if enabled and not ismatch(enabled, channel):
					continue
				if disabled and ismatch(disabled, channel):
					continue

				alloweds.append(callback)
			else:
				alloweds.append(callback)

		if event == events.COMMAND:
			command = kwargs['command']
			funcs = [c['func'] for c in alloweds if command == c['command']]
		else:
			funcs = [c['func'] for c in alloweds]

		for func in funcs:
			deferred = threads.deferToThread(lambda: func(*args, **kwargs))
			deferred.addErrback(self._failed)
	
	def _failed(self, failure):
		self.logger.error(failure)

