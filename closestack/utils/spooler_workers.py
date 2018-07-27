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
from closestack.models import VmRunning, VmTemplate
from django.core.exceptions import ObjectDoesNotExist

__author__ = 'knktc'
__version__ = '0.1'

NODE_MANAGER = NodeManager(nodes=settings.VM_NODES)
NOVNC_MANAGER = NovncManager(token_dir=settings.NOVNC_TOKEN_DIR)
# vm status
VM_RUNNING = 1
VM_FAILED = 6


def create(vm_config):
    """
    worker to create vm with template
    :param :
    :return:
    :rtype:
    """
    vm_id = vm_config.get('vm_id')
    vm_obj = VmRunning.objects.get(id=vm_id)

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

    # get vnc port if vm is started
    domain = vm_manager.get_domain_obj(vm_name=vm_name)
    if domain is not None and vm_manager.check_running_state(domain=domain):
        vm_info = vm_manager.get_info(domain=domain)

        # add novnc token
        novnc_info = NOVNC_MANAGER.add_token(host=node_info.get('host'), vnc_port=vm_info.get('vnc_port'),
                                             vm_name=vm_name)
        if novnc_info:
            novnc_token = novnc_info.get('token')
            vm_obj.vnc_token = novnc_token
            vm_obj.save()

    # close connection
    vm_manager.close()

    vm_obj.state = VM_RUNNING
    vm_obj.save()

    return True


def delete(vm_config):
    """
    delete vm
    :param :
    :return:
    :rtype:
    """
    return True

