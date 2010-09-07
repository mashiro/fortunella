#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella import Plugin
from fortunella.events import events
from fortunella.utils import getlogger, ClassLoader
import re

class Http(Plugin):
	def init(self, config):
		self.config = config or {}
		self.handlers = []
		self.re_url = re.compile(r'https?://[^ ]+', re.IGNORECASE|re.DOTALL)
		self.register(self._load_completed, event=events.PLUGIN_LOAD_COMPLETE)
		self.register(self.privmsg, event=events.PRIVMSG)

	def _load_completed(self):
		self.class_loader = ClassLoader(logger=self.logger, base=Handler, callback=self._handler_loaded)
		self.class_loader.loads(self.core.config.general['plugin_dir'] + '/http')

	def _handler_loaded(self, module, klass):
		name = klass.__name__
		if name in self.config:
			handler = klass(self)
			handler.init(self.config[name])
			self.handlers.append(handler)
			return True
		return False

	def privmsg(self, user, channel, message):
		pass

class Handler(object):
	def __init__(self, plugin):
		self.priority = 100
		self.logger = getlogger(self)
		self.plugin = plugin
		self.core = plugin.core
		self.notice = plugin.notice
	
	#def init(self, config):
	#def process(self, url):

