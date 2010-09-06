#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.plugin import Plugin
from fortunella.events import events
from twisted.internet import threads, reactor, defer
import os
import logging
import itertools
from glob import glob

class PluginManager(object):
	def __init__(self, core):
		self.logger = logging.getLogger('fortunella.PluginManager')
		self.core = core
		self.callbackmap = {}
		self.plugins = []
		self.path = None

	def load(self, modname):
		try:
			module = __import__(modname)
			names = itertools.ifilter(lambda name: name in self.core.config.plugins, dir(module))
			attrs = itertools.imap(lambda name: getattr(module, name), names)
			klasses = itertools.ifilter(lambda attr: isinstance(attr, type), attrs)
			klasses = itertools.ifilter(lambda klass: issubclass(klass, Plugin), klasses)
			klasses = itertools.ifilter(lambda klass: klass != Plugin, klasses)

			for klass in klasses:
				try:
					name = klass.__name__
					plugin = klass(self.core, self)
					plugin.init(self.core.config.plugins[name])
					self.plugins.append(plugin)
				except Exception, e:
					self.logger.exception('%s instance error', name)
				else:
					self.logger.info('%s plugin is loaded', name)

		except ImportError, e:
			self.logger.exception('%s import error', modname)
		except Exception, e:
			self.logger.exception('%s unknown error', modname)
	
	def loads(self, path):
		self.path = path
		for pathname in glob(os.path.join(path, '*.py')):
			name, ext = os.path.splitext(pathname)
			self.load(name)
	
	def reload(self):
		return self.loads(self.path)
	


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
			deferred.addErrback(lambda fail: fail.trap(defer.CancelledError))
			#deferred.cancel()
	
