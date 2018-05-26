#!/usr/bin/env python
# -*- coding: utf-8 -*-
# models

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-26 12:10
"""

from django.db import models
from django.contrib.postgres.fields import JSONField

__author__ = 'knktc'
__version__ = '0.1'


# VM templates
class VmTemplate(models.Model):
    name = models.CharField(max_length=64, unique=True)
    enable = models.BooleanField(default=True)
    image_path = models.CharField(max_length=1024)
    # required vm config
    config = JSONField()
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True, blank=True)


# store recorded VMs' info
class VmRunning(models.Model):
    name = models.CharField(max_length=64, unique=True)
    template = models.ForeignKey(VmTemplate, on_delete=models.PROTECT)
    state = models.IntegerField(choices=(
        (0, 'pending'),
        (1, 'stopped'),
        (2, 'running'),
        (3, 'destroyed'),
        (4, 'discard'),
        (5, 'deleted'),
    ), default=0)
    node = JSONField()
    image_path = models.CharField(max_length=1024)
    config = JSONField()
    vnc = JSONField(blank=True, null=True)
    create_time = models.DateTimeField()
    update_time = models.DateTimeField(auto_now=True)
    note = models.TextField(null=True, blank=True)
