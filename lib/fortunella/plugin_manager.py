#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.plugin import Plugin
import sys
import os
from glob import glob

class PluginManager(object):
	def __init__(self, core):
		self.core = core
		self.logger = core.logger
		self.plugins = []

	def load(self, filename):
		try:
			name, ext = os.path.splitext(filename)
			module = __import__(name, globals(), locals())
			for name in dir(module):
				klass = getattr(module, name)
				if isinstance(klass, type) and klass != Plugin and issubclass(klass, Plugin):
					try:
						plugin = klass(self.core)
						self.plugins.append(plugin)
					except Exception, e:
						self.logger.exception('%s instance error', name)
					else:
						self.logger.info('%s plugin is loaded.', name)

		except ImportError, e:
			self.logger.exception('%s import error', name)
		except Exception, e:
			self.logger.exception('%s unknown error', name)

	def loads(self, path=None):
		if path is None:
			path = self.core.general_config['plugins_dir']
		for filename in glob(os.path.join(path, '*.py')):
			self.load(filename)
	
