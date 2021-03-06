#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fortunella.plugin import Plugin
from fortunella.events import events
from fortunella.utils import getlogger, ClassLoader, isallowed, fullname
from twisted.internet import threads, reactor, defer
import sys
import os
import re
import imp

class PluginManager(object):
    def __init__(self, core):
        self.logger = getlogger(self)
        self.core = core
        self.callbackmap = {}
        self.plugins = []

        # create plugins dummy module.
        self.plugin_module_name = 'fortunella.plugins'
        sys.modules[self.plugin_module_name] = imp.new_module(self.plugin_module_name)
        self.class_loader = ClassLoader(logger=self.logger, base=Plugin, callback=self._plugin_loaded)

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
        elif hasattr(func, '__self__'):
            instance = func.__self__
        else:
            instance = None

        callbacks = self.callbackmap.setdefault(event, [])
        callbacks.append(dict(instance=instance, func=func, command=command))
        self.logger.debug('registering %s for event %s', func, events.name(event))
        return self

    def datafile(self, instance, filename):
        name = instance.__class__.__name__
        head, tail = os.path.split(filename)
        dirname = os.path.join(self.core.config.general['data_dir'], name, head)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        return os.path.join(dirname, tail)

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
                config = self.core.config.plugins[klass.__name__] or {}
                if not isallowed(config, channel):
                    continue
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

