#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from setuptools import setup
import sys

major, minor, micro, releaselevel, serial = sys.version_info

requires = []
requires.append('Twisted')
requires.append('PyYAML')
requires.append('PIL')
if major == 2 and minor <= 4:
	requires.append('elementTree')
if major == 2 and minor <= 5:
	requires.append('simplejson')

setup(
	name='fortunella',
	version='0.1.0',
	install_requires=requires)

