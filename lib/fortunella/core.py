#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from fortunella.plugin import Plugin
from fortunella.plugin_manager import PluginManager
import sys
import os
import logging
from glob import glob

class Core(irc.IRCClient):
	def connectionMade(self):
		self.logger = self.factory.logger
		self.config = self.factory.config
		self.general_config = self.config['general']
		self.plugins_config = self.config['plugins']

		# connect
		self.nickname = self.general_config['nickname']
		self.password = self.general_config['password']
		irc.IRCClient.connectionMade(self)
		self.logger.info('connected.')

		# load plugins
		self.plugin_manager = PluginManager(self)
		self.plugin_manager.loads()

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.info('disconnected.')

	def privmsg(self, user, channel, msg):
		user = user.split('!', 1)[0]
		self.logger.debug('<%s> %s: %s', channel, user, msg)
	
	def noticed(self, user, channel, msg):
		pass


class CoreFactory(protocol.ReconnectingClientFactory):
	protocol = Core

	def __init__(self, config, logger):
		self.config = config
		self.logger = logger
	
	def clientConnectionLost(self, connector, reason):
		self.logger.debug('disconnected: %s', reason)
		protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
	
	def clientConnectionFailed(self, connector, reason):
		self.logger.debug('connection failed: %s', reason)
		protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)


def run(config={}, logger=None):
	if logger is None:
		stdout_handler = logging.StreamHandler(sys.stdout)
		formatter = logging.Formatter('%(asctime)s [%(module)s] %(message)s', '%Y-%m-%d %H:%M:%S')
		stdout_handler.setFormatter(formatter)
		logger = logging.getLogger('fortunella')
		logger.addHandler(stdout_handler)
		logger.setLevel(logging.DEBUG)

	general = config.setdefault('general', {})
	plugins = config.setdefault('plugins', {})
	host = general.setdefault('host', 'localhost')
	port = general.setdefault('port', 6667)
	general.setdefault('nickname', 'fortunella')
	general.setdefault('password', '')
	general.setdefault('plugins_dir', 'plugins')

	reactor.connectTCP(host, port, CoreFactory(config, logger))
	reactor.run()

