#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from fortunella.plugins.http import Handler

class Default(Handler):
	def init(self, config):
		self.priority = 0
	
	def process(self, url):
		return url


