#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-26 13:26
"""

from django.conf import settings
from django.http import JsonResponse

__author__ = 'knktc'
__version__ = '0.1'

ERRORS = settings.ERRORS


def success(data=None, msg=None):
    """
    return success result
    :param data: data
    :param msg: additional message(if any)
    :return: success result
    :rtype: JsonResponse
    """
    result = {'status': 0}
    if data is not None:
        result['data'] = data
    if msg is not None:
        result['msg'] = msg
    return JsonResponse(result)


def failed(status, data=None, msg=None):
    """
    return faild result
    :param status: status code
    :param data: data(if any)
    :param msg: additional message
    :return: failed result
    :rtype: JsonResponse
    """
    result = {'status': status}
    if data is not None:
        result['data'] = data

    if msg is not None:
        result['msg'] = msg
    else:
        result['msg'] = ERRORS.get(status)

    return JsonResponse(result)
