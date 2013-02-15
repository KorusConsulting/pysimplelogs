# -*- coding: utf-8 -*-

import multiprocessing
import requests
import time
import json
import os

from config import SLEEP_TIME, NUMBER_OF_ATTEMPTS, CONNECTION_TIMEOUT


class Worker:
    def __init__(self, level, owner, data, url, tags=[]):
        self.level = level
        self.owner = owner
        self.data = data
        self.tags = tags
        self.url = url

    def send(self):
        url = self.url + '/api/entry/'
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data_for_posting = {'level': self.level,
                            'owner': self.owner,
                            'data': self.data,
                            'tags': self.tags}
        attempts = NUMBER_OF_ATTEMPTS
        request = False
        while attempts:
            try:
                request = requests.post(url,
                                        data=json.dumps(data_for_posting),
                                        headers=headers,
                                        timeout=CONNECTION_TIMEOUT)
                break
            except:
                attempts -= 1
                time.sleep(SLEEP_TIME)
        return request


class Transplant:
    def __init__(self, method, host, url, method_name=None):
        self.host = host
        self.method = method
        self.url = url
        self.method_name = method_name or method.__name__
        setattr(host, method_name or method.__name__, self)

    def __call__(self, *args, **kwargs):
        nargs = [self]
        nargs.extend(args)
        return apply(self.method, nargs, kwargs)


def get_levels_list(url):
    try:
        levels = json.loads(requests.get(os.path.join(url + "/api/level/"), timeout=CONNECTION_TIMEOUT).content)
    except:
        levels = {u'level': [u'critical', u'error', u'warning', u'notice', u'info', u'debug']}
    return levels


class Simplelog:
    def __init__(self, url):
        self.url = url
        self.init_levels()

    def init_levels(self):
        levels = get_levels_list(self.url)['level']
        for level in levels:
            Transplant(send, Simplelog, url=self.url, method_name=level)

def send(self, owner, data, tags=[]):
    worker = Worker(self.method_name, owner, data, self.url, tags)
    #TODO Add queue.
    multiprocessing.Process(target=worker.send).start()
    return