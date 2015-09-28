# -*- coding: utf-8 -*-

import multiprocessing
import time
import json
from datetime import datetime, date

import requests

from config import SLEEP_TIME, NUMBER_OF_ATTEMPTS, CONNECTION_TIMEOUT


class APIEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, date):
            return date.strftime(obj, "%Y-%m-%d")
        else:
            return super(APIEncoder, self).default(obj)


class Worker(object):
    """Worker for multiprocessing. It can send new log entry to simplelogs server.

    Keyword arguments:
    owner -- user or system, who try to create entry (required).
    level -- message level: info, warning, error, etc.
    data -- all other information (required).
    url -- simplelogs server URI.
    tags -- tags for current entry.

    """
    def __init__(self, level, owner, data, url, tags=[]):
        self.level = level
        self.owner = owner
        self.data = data
        self.tags = tags
        self.url = url

    def send(self):
        """ New entry creator.

        This method creating new entry and trying to send it to remote server.
        It use 3 params SLEEP_TIME, NUMBER_OF_ATTEMPTS, CONNECTION_TIMEOUT from config-fle.
        For more detail about this params, please, read comment in config.py/

        """
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


class Transplant(object):
    """Class-methods fabric.

    Keyword arguments:
    host -- сlass, which will be transplanted.
    method -- function or static method that will be new method in 'host'.
    method_name -- by default the new class-method will have the same name as method,
     if you want to change it, you should specify 'method_name' (not required)

    This class can create any method with any name based on other class method or function in any class.

    """
    def __init__(self, method, host, url=None, method_name=None):
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
    """Returns levels from server or default-list if server is unavailable."""
    try:
        levels = json.loads(requests.get(url + "/api/level/", timeout=CONNECTION_TIMEOUT).content)
    except:
        levels = {u'level': [u'critical', u'error', u'warning', u'notice', u'info', u'debug']}
    return levels


class Simplelog(object):
    """Basic class for lib users.

    Keyword arguments:
    url -- simplelogs server URI.

    Instance of this class is transplanting to them self methods from http://hostname/api/level/ list
     and give to lib users all of message levels as a class methods.

    """
    def __init__(self, url):
        self.url = url
        self.init_levels()

    def init_levels(self):
        levels = get_levels_list(self.url)['level']
        for level in levels:
            Transplant(send, Simplelog, url=self.url, method_name=level)

    def get_owners(self):
        try:
            response = requests.get(self.url + "/api/owners/", timeout=CONNECTION_TIMEOUT)
        except requests.ConnectionError, e:
            print e
        else:
            if response.status_code == requests.codes.ok:
                try:
                    result = response.json()
                except ValueError, e:
                    print e
                else:
                    return result
        return None

    def get_list(self, **kwargs):
        params = dict()
        if kwargs:
            if 'find' in kwargs:
                params['find'] = kwargs['find']
            if 'sort' in kwargs:
                params['sort'] = kwargs['sort']
            if 'limit' in kwargs:
                params['limit'] = kwargs['limit']
            if 'skip' in kwargs:
                params['skip'] = kwargs['skip']
            try:
                response = requests.post(self.url + "/api/list/",
                                         headers={'content-type': 'application/json'},
                                         data=json.dumps(params, cls=APIEncoder),
                                         timeout=CONNECTION_TIMEOUT)
            except requests.ConnectionError, e:
                print e
                return None
        else:
            try:
                response = requests.get(self.url + "/api/list/",
                                        headers={'content-type': 'application/json'},
                                        timeout=CONNECTION_TIMEOUT)
            except requests.ConnectionError, e:
                print e
                return None
        if response.status_code == requests.codes.ok:
            try:
                result = response.json()
            except ValueError, e:
                print e
            else:
                return result
        return None

    def count(self, **kwargs):
        params = dict()
        if kwargs:
            if 'find' in kwargs:
                params['find'] = kwargs['find']
            if 'sort' in kwargs:
                params['sort'] = kwargs['sort']
            if 'limit' in kwargs:
                params['limit'] = kwargs['limit']
            try:
                response = requests.post(self.url + "/api/count/",
                                         headers={'content-type': 'application/json'},
                                         data=json.dumps(params, cls=APIEncoder),
                                         timeout=CONNECTION_TIMEOUT)
            except requests.ConnectionError, e:
                print e
                return None
        else:
            try:
                response = requests.get(self.url + "/api/count/",
                                        headers={'content-type': 'application/json'},
                                        timeout=CONNECTION_TIMEOUT)
            except requests.ConnectionError, e:
                print e
                return None
        if response.status_code == requests.codes.ok:
            try:
                result = response.json()
            except ValueError, e:
                print e
            else:
                return result
        return None


def send(self, owner, data, tags=[]):
    """Creating worker for sending message as a new process and return."""
    worker = Worker(self.method_name, owner, data, self.url, tags)
    #TODO Add queue.
    try:
        multiprocessing.Process(target=worker.send).start()
    except AssertionError as e:
        # https://github.com/celery/celery/issues/1709
        print e
        worker.send()
    return