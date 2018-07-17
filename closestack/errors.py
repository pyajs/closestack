#!/usr/bin/env python
# -*- coding: utf-8 -*-
# error codes

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-18 21:58
"""

__author__ = 'knktc'
__version__ = '0.1'


ERRORS = {
    # success
    0: 'success',

    # global errors
    1000000: 'unknown error',
    1000001: 'malformed requests',

    # vm template api errors
    1001001: 'vm template names duplicated',

    # vm manager api errors
    1002001: 'template not exists',
    1002002: 'cpu does not reach minimum requirements',
    1002003: 'memory doest not reach minimum requirements',
    1002004: 'host_passthrough config needed',
    1002005: 'vm name duplicated',
    1002006: 'node connection failed',
    1002007: 'create running image failed',


}
