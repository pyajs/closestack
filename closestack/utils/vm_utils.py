#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vm manager

"""
@author:knktc
@contact:me@knktc.com
@create:2018-06-03 22:53
"""

import libvirt
from .utils import cmd_runner, format_vm_xml
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
                 qemu_kvm_exec, template_path, ssh_path='/usr/bin/ssh'):
        """
        connect to host
        :param :
        :return:
        :rtype:
        """
        self.conn_str = conn_str
        self.qemu_img_exec = qemu_img_exec
        self.qemu_kvm_exec = qemu_kvm_exec
        self.ssh_path = ssh_path

        # get template
        try:
            with open(template_path, 'r') as f:
                self.template = f.read()
        except Exception as e:
            raise VmManagerError("vm template file open failed")

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
        except Exception as e:
            return None

    def check_vm_existence(self, vm_name):
        """
        check vm existence
        :param vm_name: vm name string
        :return: domain object or None
        :rtype: object
        """
        return self.get_domain_obj(vm_name=vm_name)

    def create_image(self, base_image_path, new_image_path, host, ssh_port, ssh_user, timeout=120):
        """
        create image by base image, will use ssh to connect to other hosts and run commands
        :param timeout: command timeout
        :param ssh_user: ssh user
        :param ssh_port: ssh port
        :param host: the host we want to create image on
        :param base_image_path: base image path
        :param new_image_path: new image path
        :return: boolean result of creation
        :rtype: bool
        """
        cmd = '{} create -b {} -f qcow2 {}'.format(self.qemu_img_exec, base_image_path, new_image_path)
        cmd = "{} -p {} {}@{} {}".format(self.ssh_path, ssh_port, ssh_user, host, cmd)
        code, stdout, stderr = cmd_runner(cmd=cmd, timeout=timeout)
        if code == 0:
            return True
        else:
            return False

    def define(self, vm_name, image_path, cpu_cores=1, memory=524288, host_passthrough=False,
               persistent=False, boot=True):
        """
        define or create vm by xml

        :param vm_name: vm name string
        :param image_path: the vm will run with this image
        :param cpu_cores: cpu cores
        :param memory: ram size
        :param host_passthrough: if true, we will set host passthrough to vm xml
        :param persistent: persistent or not
        :param boot: if true, the vm will boot after vm defined
        :return: status code
        :rtype: int

        status
        ========
        0: success
        1: xml format failed
        2: create vm failed, unknown reason
        3: vm successfully defined, but boot failed'

        """
        # config dict
        config_dict = {
            'vm_name': vm_name,
            'image_path': image_path,
            'qemu_kvm_exec': self.qemu_kvm_exec,
            'memory': memory,
            'current_memory': memory,
            'cpu_cores': cpu_cores,
        }

        # add host passthrough config
        if host_passthrough:
            config_dict['host_passthrought'] = "<cpu mode='host-passthrough' check='none'/>"
        else:
            config_dict['host_passthrought'] = ''

        # format xml
        xml_config = format_vm_xml(template=self.template, config_dict=config_dict)
        if xml_config:
            return 1

        # create vm
        try:
            if not persistent:
                dom = self.conn.createXML(xml_config, 0)
            else:
                dom = self.conn.defineXML(xml_config)
            if dom is None:
                return 2
        except Exception as e:
            return 2

        # try to boot vm
        if persistent and boot:
            if dom.create() < 0:
                return 3
            else:
                return 0
        else:
            return 0

