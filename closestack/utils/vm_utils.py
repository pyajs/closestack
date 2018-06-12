#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vm manager

"""
@author:knktc
@contact:me@knktc.com
@create:2018-06-03 22:53
"""

import libvirt
from xml.etree import ElementTree

__author__ = 'knktc'
__version__ = '0.1'


class VmManagerError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class VmManager(object):
    def __init__(self, conn_str, qemu_img_exec,
                 qemu_kvm_exec):
        """
        connect to host
        :param :
        :return:
        :rtype:
        """
        self.conn_str = conn_str
        self.qemu_img_exec = qemu_img_exec
        self.qemu_kvm_exec = qemu_kvm_exec

        # try to connect to hypervisor
        self.conn = libvirt.open(self.conn_str)
        if self.conn is None:
            raise VmManagerError("connection failed, conn string: {}".format(self.conn_str))

    def close(self):
        """
        close connection
        """
        self.conn.close()

    def get_domain_obj(self, vm_name):
        """
        get domain object by vm_name, will return domain object or None
        :param vm_name: vm name string
        :return: domain object or None
        :rtype: object
        """
        try:
            domain = self.conn.lookupByName(vm_name)
            return domain
        except:
            return None



