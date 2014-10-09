# -*- coding: utf-8 -*-

import logging
from pysimplelogs import Simplelog, requests


class SimplelogHandler(logging.Handler):

    def __init__(self, url, owner):
        logging.Handler.__init__(self)
        self.url = url
        self.owner = owner

    def emit(self, record):
        message = self.format(record)
        client = Simplelog(self.url)
        level = record.levelname.lower()
        if not hasattr(client, level):
            level = 'debug'
        tags = list()
        if hasattr(record, 'tags'):
            tags = getattr(record, 'tags')
        getattr(client, level)(self.owner, message, tags)


class SimpleLogger(object):

    @classmethod
    def __check_url(cls, url):
        try:
            r = requests.get('{0}/api/'.format(url), timeout=2)
            if r.status_code == 200:
                return True
        except requests.RequestException, e:
            print u'Couldn\'t connect to simplelogs ({0})'.format(e)
        return False

    @classmethod
    def __log_except(cls, _logger, debug_mode=False):
        #TODO: Нужно ли?! не будет ли зацикливания?
        if not debug_mode:
            # write to log all unhandled exceptions if not DEBUG mode
            import sys
            import traceback

            def log_except_hook(*exc_info):
                text = "".join(traceback.format_exception(*exc_info))
                _logger.error("Unhandled exception: %s", text)

            sys.excepthook = log_except_hook

    @classmethod
    def get_logger(cls, url, module_name, owner, debug_mode=False):
        _logger = logging.getLogger(module_name)
        _logger.setLevel(logging.DEBUG)

        if cls.__check_url(url):
            # create handler
            handler = SimplelogHandler(url, owner)
            # create formatter
            formatter = logging.Formatter(u'%(module) - %(funcName)s - %(asctime)s - %(levelname)s - %(message)s')
        else:
            # create handler and set level to debug
            handler = logging.StreamHandler()
            # create formatter
            formatter = logging.Formatter(u'%(module) - %(funcName)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # set handler level to debug
        handler.setLevel(logging.DEBUG)
        # add formatter to handler
        handler.setFormatter(formatter)

        _logger.addHandler(handler)

        cls.__log_except(_logger, debug_mode)

        return _logger
