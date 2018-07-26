#!/usr/bin/env python
# -*- coding: utf-8 -*-
# async tasks with uwsgi spooler

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-26 13:40
"""

import json
import uwsgi
from closestack.utils import spooler_workers

__author__ = 'knktc'
__version__ = '0.1'


def worker_dispatcher(arguments):
    """
    dispatcher for spooler
    :param arguments: spooler arguments
    :return: spool status
    :rtype: object
    """
    config = json.loads(arguments.get('body').decode('utf8'))
    action = config.get('action')
    print(getattr(spooler_workers, action)(config))

    return uwsgi.SPOOL_OK


uwsgi.spooler = worker_dispatcher
