#!/usr/bin/env python
# -*- encoding: utf-8 -*-

class Plugin(object):
	def __init__(self, core):
		self.core = core
		self.logger = core.logger

