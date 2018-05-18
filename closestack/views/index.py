#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-14 13:30
"""

from django.shortcuts import render_to_response

__author__ = 'knktc'
__version__ = '0.1'


def index(request):
    """
    show index page
    :param :
    :return:
    :rtype:
    """
    return render_to_response('index.html')
