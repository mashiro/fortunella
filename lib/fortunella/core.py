#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from fortunella.plugin_manager import PluginManager
from fortunella.plugin import Plugin
from fortunella.events import events
import sys
import logging
import inspect

class Core(irc.IRCClient):

	def info(self, fmt, *args, **kwargs):
		self.writelog(self.logger.info, fmt, *args, **kwargs)
	
	def debug(self, fmt, *args, **kwargs):
		self.writelog(self.logger.debug, fmt, *args, **kwargs)

	def writelog(self, func, fmt, *args, **kwargs):
		channel = kwargs.setdefault('channel', 'fortunella')
		func('<%s> %s', channel, fmt % args)


	def lineReceived(self, line):
		if isinstance(line, str):
			line = line.decode(self.encoding, 'replace')
		irc.IRCClient.lineReceived(self, line)

	def sendLine(self, line):
		if isinstance(line, unicode):
			line = line.encode(self.encoding, 'replace')
		irc.IRCClient.sendLine(self, line)


	def connectionMade(self):
		self.logger = self.factory.logger
		self.config = self.factory.config
		self.general_config = self.config['general']
		self.plugins_config = self.config['plugins']
		self.host = self.general_config['host']
		self.port = self.general_config['port']
		self.encoding = self.general_config['encoding']

		# connect
		self.nickname = self.general_config['nickname']
		self.password = self.general_config['password']
		irc.IRCClient.connectionMade(self)
		self.info('connected')

		# load plugins
		self.plugin_manager = PluginManager(self)
		self.plugin_manager.loads()
		self.plugin_manager.push(events.CONNECTIN_MADE)

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.info('disconnected')
		self.plugin_manager.push(events.CONNECTIN_LOST, reason=reason)

	def signedOn(self):
		self.info('signed on')
		self.plugin_manager.push(events.SIGNED_ON)


	def joined(self, channel):
		self.userJoined(self.nickname, channel)

	def userJoined(self, user, channel):
		self.debug('%s has joined', user, channel=channel)
		self.plugin_manager.push(events.JOIN, user=user, channel=channel)

	def left(self, channel):
		self.userLeft(self.nickname, channel)

	def userLeft(self, user, channel):
		self.debug('%s has left', user, channel=channel)
		self.plugin_manager.push(events.LEFT, user=user, channel=channel)

	def userQuit(self, user, message):
		self.debug('%s has quit (%s)', user, message)
		self.plugin_manager.push(events.QUIT, user=user, message=message)

	def modeChanged(self, user, channel, added, modes, params):
		user = user.split('!', 1)[0]
		params = tuple([param for param in params if param])
		self.debug('%s has changed mode: %c%s %s', user, '+' if added else '-', modes, ' '.join(params), channel=channel)
		self.plugin_manager.push(events.MODE, user=user, channel=channel, added=added, params=params)

	def privmsg(self, user, channel, message):
		user = user.split('!', 1)[0]
		self.debug('%s: %s', user, message, channel=channel)

		if channel == self.nickname:
			self.plugin_manager.push(events.TALK, user=user, message=message)
		else:
			args = message.split()
			if len(args) >= 1:
				command = args.pop(0)
				self.plugin_manager.push(events.COMMAND, command=command, user=user, channel=channel, *args)
			self.plugin_manager.push(events.PRIVMSG, user=user, channel=channel, message=message)

	def noticed(self, user, channel, message):
		user = user.split('!', 1)[0]
		self.debug('(NOTICE) %s: %s', user, message, channel=channel)
		self.plugin_manager.push(events.NOTICE, user=user, channel=channel, message=message)

	def nickChanged(self, newnick):
		oldnick = self.nickname
		self.nickname = newnick
		self.userRenamed(oldnick, newnick)

	def userRenamed(self, oldnick, newnick):
		self.debug('%s is now known as %s', oldnick, newnick)
		self.plugin_manager.push(events.NICK, oldnick=oldnick, newnick=newnick)

	def kickedFrom(self, channel, kicker, message):
		self.userKicked(self.nickname, channel, kicker, message)

	def userKicked(self, kicked, channel, kicker, message):
		self.debug('%s has kicked %s (%s)', kicker, kicked, message, channel=channel)
		self.plugin_manager.push(events.KICK, kicked=kicked, kicker=kicker, channel=channel, message=message)

	def topicUpdated(self, user, channel, topic):
		self.debug('%s has set topic: %s', user, topic, channel=channel)
		self.plugin_manager.push(events.TOPIC, user=user, topic=topic, channel=channel)


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
		formatter = logging.Formatter('%(asctime)s %(levelname)s [%(module)s] %(message)s', '%Y-%m-%d %H:%M:%S')
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
	general.setdefault('encoding', 'utf-8')
	general.setdefault('plugins_dir', 'plugins')

	reactor.connectTCP(host, port, CoreFactory(config, logger))
	reactor.run()

