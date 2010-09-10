#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, './lib')
import codecs
import yaml
import optparse
import logging
import locale
import fortunella.core

LOG_LEVELS = dict(
    debug=logging.DEBUG,
    info=logging.INFO,
    warning=logging.WARNING,
    error=logging.ERROR,
    critical=logging.CRITICAL)

def wrapstdio():
    enc = sys.getfilesystemencoding()
    sys.stdin = codecs.getreader(enc)(sys.stdin, 'replace')
    sys.stdout = codecs.getwriter(enc)(sys.stdout, 'replace')

def setuplogger(config):
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    stdout_handler.setFormatter(formatter)
    logger = logging.getLogger('fortunella')
    logger.addHandler(stdout_handler)
    loglevel = config['general'].get('loglevel', '')
    logger.setLevel(LOG_LEVELS.get(loglevel, logging.INFO))

def main(config):
    setuplogger(config)
    fortunella.core.run(config)

if __name__ == '__main__':
    locale.setlocale(locale.LC_ALL, '')
    wrapstdio()

    parser = optparse.OptionParser()
    parser.add_option('-c', '--config', dest='config', default='config.yaml', help='config filename')
    options, args = parser.parse_args()

    config = yaml.load(open(options.config))
    general = config.setdefault('general', {})

    main(config)

