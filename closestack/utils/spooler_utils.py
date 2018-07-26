#!/usr/bin/env python
# -*- coding: utf-8 -*-
# utils for uwsgi spooler

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-26 13:42
"""

import os
import uwsgi
import json
from django.conf import settings

__author__ = 'knktc'
__version__ = '0.1'


# config
def add_task(queue, data):
    """

    :param :
    :return:
    :rtype:
    """
    body = json.dumps(data).encode(encoding='utf8')
    spooler = os.path.join(settings.SPOOLER_DIR, queue).encode(encoding='utf8')
    try:
        uwsgi.spool({
            b'body': body,
            b'spooler': spooler,
        })
        return True
    except Exception as e:
        return False
