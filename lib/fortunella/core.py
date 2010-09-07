#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.plugin_manager import PluginManager
from fortunella.events import events
from fortunella.utils import getlogger
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

class Config(object):
	def __init__(self, d):
		self.general = d['general']
		self.plugins = d['plugins']

class Core(irc.IRCClient):
	def __init__(self):
		self.logger = getlogger(self)
		self.plugin_manager = PluginManager(self)


	def lineReceived(self, line):
		if isinstance(line, str):
			line = line.decode(self.encoding, 'replace')
		irc.IRCClient.lineReceived(self, line)

	def sendLine(self, line):
		if isinstance(line, unicode):
			line = line.encode(self.encoding, 'replace')
		irc.IRCClient.sendLine(self, line)


	def connectionMade(self):
		self.config = self.factory.config
		self.host = self.config.general['host']
		self.port = self.config.general['port']
		self.encoding = self.config.general['encoding']

		# connect
		self.nickname = self.config.general['nickname']
		self.password = self.config.general['password']
		irc.IRCClient.connectionMade(self)
		self.logger.info('connected')

		# load plugins
		self.plugin_manager.loads(self.config.general['plugin_dir'])
		self.plugin_manager.push(events.CONNECTION_MADE)

	def connectionLost(self, reason):
		irc.IRCClient.connectionLost(self, reason)
		self.logger.info('disconnected')
		self.plugin_manager.push(events.CONNECTION_LOST, reason=reason)

	def signedOn(self):
		self.logger.info('signed on')
		self.plugin_manager.push(events.SIGNED_ON)


	def joined(self, channel):
		self.userJoined(self.nickname, channel)

	def userJoined(self, user, channel):
		self.logger.debug('<%s> %s has joined', channel, user)
		self.plugin_manager.push(events.JOIN, user=user, channel=channel)

	def left(self, channel):
		self.userLeft(self.nickname, channel)

	def userLeft(self, user, channel):
		self.logger.debug('<%s> %s has left', channel, user)
		self.plugin_manager.push(events.LEFT, user=user, channel=channel)

	def userQuit(self, user, message):
		self.logger.debug('%s has quit (%s)', user, message)
		self.plugin_manager.push(events.QUIT, user=user, message=message)

	def modeChanged(self, user, channel, added, modes, params):
		user = user.split('!', 1)[0]
		params = tuple([param for param in params if param])
		self.logger.debug('<%s> %s has changed mode: %c%s %s', channel, user, '+' if added else '-', modes, ' '.join(params))
		self.plugin_manager.push(events.MODE, user=user, channel=channel, added=added, params=params)

	def privmsg(self, user, channel, message):
		user = user.split('!', 1)[0]
		self.logger.debug('<%s> %s: %s', channel, user, message)

		if channel == self.nickname:
			self.plugin_manager.push(events.TALK, user=user, message=message)
		else:
			params = message.split()
			if len(params) >= 1:
				command = params.pop(0)
				self.plugin_manager.push(events.COMMAND, command=command, user=user, channel=channel, params=params)
			self.plugin_manager.push(events.PRIVMSG, user=user, channel=channel, message=message)

	def noticed(self, user, channel, message):
		user = user.split('!', 1)[0]
		self.logger.debug('(NOTICE) <%s> %s: %s', channel, user, message)
		self.plugin_manager.push(events.NOTICE, user=user, channel=channel, message=message)

	def nickChanged(self, newnick):
		oldnick = self.nickname
		self.nickname = newnick
		self.userRenamed(oldnick, newnick)

	def userRenamed(self, oldnick, newnick):
		self.logger.debug('%s is now known as %s', oldnick, newnick)
		self.plugin_manager.push(events.NICK, oldnick=oldnick, newnick=newnick)

	def kickedFrom(self, channel, kicker, message):
		self.userKicked(self.nickname, channel, kicker, message)

	def userKicked(self, kicked, channel, kicker, message):
		self.logger.debug('<%s> %s has kicked %s (%s)', channel, kicker, kicked, message)
		self.plugin_manager.push(events.KICK, kicked=kicked, kicker=kicker, channel=channel, message=message)

	def topicUpdated(self, user, channel, topic):
		self.logger.debug('<%s> %s has set topic: %s', channel, user, topic)
		self.plugin_manager.push(events.TOPIC, user=user, topic=topic, channel=channel)

class CoreFactory(protocol.ReconnectingClientFactory):
	protocol = Core

	def __init__(self, config):
		self.config = config
		self.logger = getlogger(self)
	
	def clientConnectionLost(self, connector, reason):
		self.logger.debug('connection lost: %s', reason)
		protocol.ReconnectingClientFactory.clientConnectionLost(self, connector, reason)
	
	def clientConnectionFailed(self, connector, reason):
		self.logger.debug('connection failed: %s', reason)
		protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

def setdefault(config):
	general = config.setdefault('general', config.pop('general', None) or {})
	plugins = config.setdefault('plugins', config.pop('plugins', None) or {})
	general.setdefault('host', 'localhost')
	general.setdefault('port', 6667)
	general.setdefault('nickname', 'fortunella')
	general.setdefault('password', '')
	general.setdefault('encoding', 'utf-8')
	general.setdefault('plugin_dir', 'plugins')
	return config

def run(config):
	config = Config(setdefault(config))
	factory = CoreFactory(config)
	reactor.connectTCP(config.general['host'], config.general['port'], factory)
	reactor.run()

