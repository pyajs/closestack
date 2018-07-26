#!/usr/bin/env python
# -*- coding: utf-8 -*-
# models

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-26 12:10
"""

from django.db import models
from django.conf import settings

__author__ = 'knktc'
__version__ = '0.1'

# config
DEFAULT_VM_CONFIG = settings.DEFAULT_VM_CONFIG.copy()


# base model
class BaseModel(models.Model):
    name = models.CharField(max_length=64, unique=True)
    enable = models.BooleanField(default=True)
    image_path = models.CharField(max_length=1024)
    cpu = models.IntegerField(default=DEFAULT_VM_CONFIG.get('cpu', 1))
    memory = models.IntegerField(default=DEFAULT_VM_CONFIG.get('memory', 524288))
    host_passthrough = models.BooleanField(default=DEFAULT_VM_CONFIG.get('host_passthrough', False))
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


# VM templates
class VmTemplate(BaseModel):
    pass


# store recorded VMs' info
class VmRunning(BaseModel):
    name = models.CharField(max_length=64)
    vm_name = models.CharField(max_length=36, blank=True, null=True)
    enable = None
    template = models.ForeignKey(VmTemplate, on_delete=models.PROTECT)
    state = models.IntegerField(choices=(
        (0, 'pending'),
        (1, 'stopped'),
        (2, 'running'),
        (3, 'destroyed'),
        (4, 'discard'),
        (5, 'deleted'),
        (6, 'failed'),
    ), default=0)
    persistent = models.BooleanField(default=True)
    node = models.CharField(max_length=1024, blank=True, null=True)
    vnc_token = models.CharField(max_length=64)
