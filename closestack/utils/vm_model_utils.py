#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-27 15:38
"""

from closestack.models import VmRunning, VmTemplate
from django.core.exceptions import ObjectDoesNotExist

__author__ = 'knktc'
__version__ = '0.1'


def get_vm_obj(vm_id):
    """ 
    get vm object by id
    :param :  
    :return:
    :rtype: 
    """
    try:
        vm_obj = VmRunning.objects.get(id=vm_id)
        return vm_obj
    except ObjectDoesNotExist:
        return None

