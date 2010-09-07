#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import re
import os
import logging
import itertools
from glob import glob

def getlogger(instance):
	klass = instance.__class__
	names = re.split(r'[/\.]', klass.__module__)
	if 'fortunella' != names[0]:
		names.pop(0)
		names.insert(0, 'fortunella')
		names.insert(1, 'plugins')
	names.append(klass.__name__)
	return logging.getLogger('.'.join(names))

class ClassLoader(object):
	def __init__(self, logger=None, base=None, callback=None):
		self.logger = logger or getlogger(self)
		self.base = base
		self.callback = callback
		self.path = None

	def load(self, modname):
		try:
			module = __import__(modname)
			attrs = itertools.imap(lambda name: getattr(module, name), dir(module))
			klasses = itertools.ifilter(lambda attr: isinstance(attr, type), attrs)
			if self.base:
				klasses = itertools.ifilter(lambda klass: issubclass(klass, self.base), klasses)
				klasses = itertools.ifilter(lambda klass: klass != self.base, klasses)

			for klass in klasses:
				try:
					name = klass.__name__
					if self.callback and self.callback(module, klass):
						names = [name]
						if self.base: names.append(self.base.__name__.lower())
						self.logger.info('%s is loaded', ' '.join(names))
				except Exception, e:
					self.logger.exception('%s instance error', name)

		except ImportError, e:
			self.logger.exception('%s import error', modname)
		except Exception, e:
			self.logger.exception('%s unknown error', modname)
	
	def loads(self, path):
		self.path = path
		for pathname in glob(os.path.join(path, '*')):
			name, ext = os.path.splitext(pathname)
			if ext =='' or ext == '.py':
				self.load(name)
	
	def reload(self):
		loads(self.path)

