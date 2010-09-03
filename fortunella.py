#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
sys.path.insert(0, './lib')
import yaml
import optparse
import fortunella

def main(config):
	fortunella.run(config)

if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.add_option('-c', '--config', dest='config', default='config.yaml', help='config filename')
	options, args = parser.parse_args()
	config = yaml.load(open(options.config))
	main(config)

