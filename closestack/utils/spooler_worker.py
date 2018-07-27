#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-26 17:23
"""

import os
import uuid
import json
from django.conf import settings
from closestack.utils.vm_utils import VmManagerError, VmManager
from closestack.utils.node_utils import NodeManager
from closestack.utils.novnc_utils import NovncManager
from closestack.utils import vm_model_utils

__author__ = 'knktc'
__version__ = '0.1'

NODE_MANAGER = NodeManager(nodes=settings.VM_NODES)
NOVNC_MANAGER = NovncManager(token_dir=settings.NOVNC_TOKEN_DIR)
# vm status
VM_STOPPED = 1
VM_RUNNING = 2
VM_DESTROYED = 3
VM_DISCARD = 4
VM_DELETED = 5
VM_FAILED = 6
VM_REBUILDING = 7


class SpoolerWorker:
    def __init__(self, vm_config):
        """
        init
        :param :
        :return:
        :rtype:
        """
        self.vm_config = vm_config
        self.vm_id = vm_config.get('vm_id')
        self.vm_obj = vm_model_utils.get_vm_obj(vm_id=self.vm_id)
        self.node_info = json.loads(self.vm_obj.node) if self.vm_obj.node is not None else None

    def connect_node(self, node_info):
        """

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
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'connect to node failed'
            self.vm_obj.save()
            return None

    def get_domain(self, vm_manager):
        """
        get domain object
        :param :
        :return:
        :rtype:
        """
        domain = vm_manager.get_domain_obj(vm_name=self.vm_obj.vm_name)
        if not domain:
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'no such vm in node'
            self.vm_obj.save()
            return None
        else:
            return domain

    def create(self):
        """
        create vm
        :param :
        :return:
        :rtype:
        """
        # get node by vm name(uuid)
        vm_name = str(uuid.uuid4())
        node_info = NODE_MANAGER.get_node(key=vm_name)
        self.vm_obj.node = json.dumps(node_info)

        vm_manager = self.connect_node(node_info=node_info)

        # create image
        base_image_path = self.vm_config.get('base_image_path')
        base_image_path = os.path.join(node_info.get('image_dir'), base_image_path)
        running_image_path = os.path.join(node_info.get('running_image_dir'), '{}.img'.format(str(uuid.uuid4())))

        status = vm_manager.create_image(base_image_path=base_image_path, new_image_path=running_image_path,
                                         host=node_info.get('host'),
                                         ssh_user=node_info.get('ssh_user'),
                                         ssh_port=node_info.get('ssh_port'),
                                         )

        # create image success, write image path
        if status:
            self.vm_obj.image_path = running_image_path
        else:
            # set vm to failed
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'create image failed'
            self.vm_obj.save()
            return False

        # define vm
        status = vm_manager.define(vm_name=vm_name, image_path=running_image_path,
                                   cpu_cores=self.vm_config.get('cpu'),
                                   memory=self.vm_config.get('memory'),
                                   host_passthrough=self.vm_config.get('host_passthrough'),
                                   persistent=self.vm_config.get('persistent'),
                                   boot=self.vm_config.get('auto_start'))
        if status == 0:
            self.vm_obj.vm_name = vm_name
        else:
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'define vm failed'
            self.vm_obj.save()
            return False

        # check vm running state
        domain = vm_manager.get_domain_obj(vm_name=vm_name)
        if domain is not None and vm_manager.check_running_state(domain=domain):
            self.vm_obj.state = VM_RUNNING
        else:
            self.vm_obj.state = VM_STOPPED

        # close connection
        vm_manager.close()

        self.vm_obj.save()

        return True


    def boot(self):
        """
        boot vm
        :param :
        :return:
        :rtype:
        """
        # connect to node
        vm_manager = self.connect_node(node_info=self.node_info)
        if not vm_manager:
            return False

        # get domain
        domain = self.get_domain(vm_manager=vm_manager)
        if not domain:
            return False

        # check running status
        running_status = vm_manager.check_running_state(domain=domain)
        if running_status:
            self.vm_obj.state = VM_RUNNING
            self.vm_obj.save()
            return True

        # boot
        status = vm_manager.start(domain=domain)
        if status:
            self.vm_obj.state = VM_RUNNING
            self.vm_obj.save()
            return True
        else:
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'vm boot failed'
            self.vm_obj.save()
            return False

    def shutdown(self):
        """
        shutdown vm
        :param :
        :return:
        :rtype:
        """
        # connect to node
        vm_manager = self.connect_node(node_info=self.node_info)

        # get domain
        domain = self.get_domain(vm_manager=vm_manager)
        if not domain:
            return False

        # check running status
        running_status = vm_manager.check_running_state(domain=domain)
        if not running_status:
            self.vm_obj.state = VM_DESTROYED
            self.vm_obj.save()
            return True

        status = vm_manager.destroy(domain=domain)
        if status:
            self.vm_obj.state = VM_DESTROYED
            self.vm_obj.save()
            return True
        else:
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'vm shutdown failed'
            self.vm_obj.save()
            return False


