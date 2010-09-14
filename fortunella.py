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

def setupenvs():
    locale.setlocale(locale.LC_ALL, '')
    enc = sys.getfilesystemencoding()
    sys.stdin = codecs.getreader(enc)(sys.stdin, 'replace')
    sys.stdout = codecs.getwriter(enc)(sys.stdout, 'replace')

def setuplogger(general):
    default_logger = logging.getLogger('fortunella')
    default_logger.setLevel(logging.DEBUG)
    default_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(name)s] %(message)s', '%Y-%m-%d %H:%M:%S')
    default_level = LOG_LEVELS.get(general.get('loglevel'), logging.INFO)

    def addhandler(handler, logger=default_logger, formatter=default_formatter, level=default_level):
        handler.setFormatter(formatter)
        handler.setLevel(level)
        logger.addHandler(handler)

    addhandler(logging.StreamHandler(sys.stdout))
    #addhandler(logging.FileHandler('log.txt', mode='a', encoding='utf-8'))

def main(config):
    setuplogger(config.get('general', {}))
    fortunella.core.run(config)

if __name__ == '__main__':
    try:
        setupenvs()

        parser = optparse.OptionParser()
        parser.add_option('-c', '--config', dest='config', default='config.yaml', help='config filename')
        options, args = parser.parse_args()

        config = yaml.load(open(options.config))
        main(config)
    except KeyboardInterrupt:
        pass

