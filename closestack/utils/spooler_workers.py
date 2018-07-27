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


def create(vm_config):
    """
    worker to create vm with template
    :param :
    :return:
    :rtype:
    """
    vm_id = vm_config.get('vm_id')
    vm_obj = vm_model_utils.get_vm_obj(vm_id=vm_id)

    # get node by vm name(uuid)
    vm_name = str(uuid.uuid4())
    node_info = NODE_MANAGER.get_node(key=vm_name)
    vm_obj.node = json.dumps(node_info)

    # try to connect to node
    try:
        vm_manager = VmManager(conn_str=node_info.get('conn'),
                               qemu_img_exec=node_info.get('qemu_img_exec'),
                               qemu_kvm_exec=node_info.get('qemu_kvm_exec'),
                               template_path=os.path.join(settings.VM_TEMPLATE_DIR, node_info.get('vm_template')),
                               ssh_path=settings.SSH_PATH)
    except VmManagerError:
        vm_obj.state = VM_FAILED
        vm_obj.note = 'connect to node failed'
        vm_obj.save()
        return False

    # create image
    base_image_path = vm_config.get('base_image_path')
    base_image_path = os.path.join(node_info.get('image_dir'), base_image_path)
    running_image_path = os.path.join(node_info.get('running_image_dir'), '{}.img'.format(str(uuid.uuid4())))

    status = vm_manager.create_image(base_image_path=base_image_path, new_image_path=running_image_path,
                                     host=node_info.get('host'),
                                     ssh_user=node_info.get('ssh_user'),
                                     ssh_port=node_info.get('ssh_port'),
                                     )

    # create image success, write image path
    if status:
        vm_obj.image_path = running_image_path
    else:
        # set vm to discard
        vm_obj.state = VM_FAILED
        vm_obj.note = 'create image failed'
        vm_obj.save()
        return False

    # define vm
    status = vm_manager.define(vm_name=vm_name, image_path=running_image_path,
                               cpu_cores=vm_config.get('cpu'),
                               memory=vm_config.get('memory'),
                               host_passthrough=vm_config.get('host_passthrough'),
                               persistent=vm_config.get('persistent'),
                               boot=vm_config.get('auto_start'))
    if status == 0:
        vm_obj.vm_name = vm_name
    else:
        vm_obj.state = VM_FAILED
        vm_obj.note = 'define vm failed'
        vm_obj.save()
        return False

    # check vm running state
    domain = vm_manager.get_domain_obj(vm_name=vm_name)
    if domain is not None and vm_manager.check_running_state(domain=domain):
        vm_obj.state = VM_RUNNING
    else:
        vm_obj.state = VM_STOPPED

    # close connection
    vm_manager.close()

    vm_obj.save()

    return True


def boot(vm_config):
    """
    boot vm
    :param :
    :return:
    :rtype:
    """
    vm_id = vm_config.get('vm_id')
    vm_obj = vm_model_utils.get_vm_obj(vm_id=vm_id)
    node_info = json.loads(vm_obj.node)

    # try to connect to node
    try:
        vm_manager = VmManager(conn_str=node_info.get('conn'),
                               qemu_img_exec=node_info.get('qemu_img_exec'),
                               qemu_kvm_exec=node_info.get('qemu_kvm_exec'),
                               template_path=os.path.join(settings.VM_TEMPLATE_DIR, node_info.get('vm_template')),
                               ssh_path=settings.SSH_PATH)
    except VmManagerError:
        vm_obj.state = VM_FAILED
        vm_obj.note = 'connect to node failed'
        return False

    # boot
    domain = vm_manager.get_domain_obj(vm_name=vm_obj.vm_name)
    status = vm_manager.start(domain=domain)
    if status:
        vm_obj.state = VM_RUNNING
        vm_obj.save()
        return True
    else:
        vm_obj.state = VM_FAILED
        vm_obj.note = 'vm boot failed'
        vm_obj.save()

