#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.plugin import Plugin
from fortunella.events import events
from twisted.internet import threads
import sys
import os
import logging
from glob import glob

class PluginManager(object):
	def __init__(self, core):
		self.core = core
		self.logger = logging.getLogger('fortunella.PluginManager')
		self.path = None
		self.plugins = []
		self.callbackmap = {}

	def load(self, filename):
		def find(module):
			config = self.core.plugins_config
			for name in dir(module):
				if not name in config:
					continue
				klass = getattr(module, name)
				if isinstance(klass, type) and klass != Plugin and issubclass(klass, Plugin):
					yield (name, klass)

		try:
			modname, ext = os.path.splitext(filename)
			module = __import__(modname, globals(), locals())
			for name, klass in find(module):
				try:
					plugin = klass(self.core, self)
					plugin.init(self.core.plugins_config[name])
					self.plugins.append(plugin)
				except Exception, e:
					self.logger.exception('%s instance error', name)
				else:
					self.logger.info('%s plugin is loaded.', name)
		except ImportError, e:
			self.logger.exception('%s import error', modname)
		except Exception, e:
			self.logger.exception('%s unknown error', modname)

	def loads(self, path):
		self.plugins = []
		self.callbackmap = {}
		self.path = path
		for filename in glob(os.path.join(self.path, '*.py')):
			self.load(filename)
	
	def reload(self):
		self.loads(self.path)
	
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
			d = threads.deferToThread(lambda: func(*args, **kwargs))


