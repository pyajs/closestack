#!/usr/bin/env python
# -*- coding: utf-8 -*-
# get remote consoles

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-30 17:55
"""

import os
import json
from closestack.utils.novnc_utils import NovncManager
from closestack.utils.vm_utils import VmManager, VmManagerError
from django.conf import settings

__author__ = 'knktc'
__version__ = '0.1'

NOVNC_MANAGER = NovncManager(token_dir=settings.NOVNC_TOKEN_DIR)
VM_RUNNING = 2


class RemoteConsoleError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class RemoteConsole:
    def __init__(self, vm_obj):
        """

        :param :
        :return:
        :rtype:
        """
        self.node_info = json.loads(vm_obj.node) if vm_obj.node is not None else None
        self.state = vm_obj.state
        self.vm_name = vm_obj.vm_name

    @staticmethod
    def connect_node(node_info):
        """
        connect to node
        :param :
        :return:
        :rtype:
        """
        try:
            vm_manager = VmManager(conn_str=node_info.get('conn'),
                                   qemu_img_exec=node_info.get('qemu_img_exec'),
                                   qemu_kvm_exec=node_info.get('qemu_kvm_exec'),
                                   template_path=os.path.join(settings.VM_TEMPLATE_DIR, node_info.get('vm_template')),
                                   ssh_path=settings.SSH_PATH)
            return vm_manager
        except VmManagerError:
            return None

    def get_domain(self, vm_manager):
        """
        get domain object
        :param :
        :return:
        :rtype:
        """
        domain = vm_manager.get_domain_obj(vm_name=self.vm_name)
        if not domain:
            return None
        else:
            return domain

    def __enter__(self):
        """
        connect to vm_manager and get domain
        :param :
        :return:
        :rtype:
        """
        # check running state
        if self.state != VM_RUNNING:
            raise RemoteConsoleError('vm is not running')

        # connect to node
        self.vm_manager = self.connect_node(node_info=self.node_info)
        if not self.vm_manager:
            raise RemoteConsoleError('can not connect to node')

        # get domain
        self.domain = self.get_domain(vm_manager=self.vm_manager)
        if not self.domain:
            raise RemoteConsoleError('no such vm')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        disconnect vm manager
        :param :
        :return:
        :rtype:
        """
        try:
            self.vm_manager.close()
        except Exception as e:
            pass

    def novnc(self):
        """ 
        get novnc
        :param :  
        :return:
        :rtype: 
        """
        # check running state
        if not self.vm_manager.check_running_state(domain=self.domain):
            raise RemoteConsoleError('vm is not running')

        # get vm info
        info = self.vm_manager.get_info(domain=self.domain)
        vnc_info = NOVNC_MANAGER.add_token(vm_name=self.vm_name,
                                           host=self.node_info.get('host'),
                                           vnc_port=info.get('vnc_port'))
        result = {
            'token': vnc_info.get('token'),
            'host': settings.NOVNC_HOST,
            'port': settings.NOVNC_PORT,
        }

        return result

