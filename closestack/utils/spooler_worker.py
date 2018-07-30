#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-26 17:23
"""

import json
import os
import uuid

from django.conf import settings

from closestack.utils import vm_model_utils, utils
from closestack.utils.node_utils import NodeManager
from closestack.utils.novnc_utils import NovncManager
from closestack.utils.vm_utils import VmManagerError, VmManager

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

    def create_vm(self, vm_name, node_info, vm_manager, vm_config):
        """
        create vm process
        :param :
        :return:
        :rtype:
        """
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
            self.vm_obj.image_path = running_image_path
        else:
            # set vm to failed
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'create image failed'
            self.vm_obj.save()
            return False

        # define vm
        status = vm_manager.define(vm_name=vm_name, image_path=running_image_path,
                                   cpu_cores=vm_config.get('cpu'),
                                   memory=vm_config.get('memory'),
                                   host_passthrough=vm_config.get('host_passthrough'),
                                   persistent=vm_config.get('persistent'),
                                   boot=vm_config.get('auto_start', True))
        if status == 0:
            self.vm_obj.vm_name = vm_name
        else:
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'define vm failed'
            self.vm_obj.save()

            # remove image
            utils.ssh_remove_file(ssh_host=node_info.get('host'),
                                  ssh_port=node_info.get('ssh_port'),
                                  ssh_user=node_info.get('ssh_user'),
                                  ssh_path=settings.SSH_PATH,
                                  file_to_remove=running_image_path)

            return False

        # check vm running state
        domain = vm_manager.get_domain_obj(vm_name=vm_name)
        if domain is not None and vm_manager.check_running_state(domain=domain):
            self.vm_obj.state = VM_RUNNING
        else:
            self.vm_obj.state = VM_STOPPED

        self.vm_obj.save()

        return True

    def create(self):
        """
        create vm action
        :param :
        :return:
        :rtype:
        """
        # get node by vm name(uuid)
        vm_name = str(uuid.uuid4())
        node_info = NODE_MANAGER.get_node(key=vm_name)
        self.vm_obj.node = json.dumps(node_info)

        vm_manager = self.connect_node(node_info=node_info)

        status = self.create_vm(vm_name=vm_name,
                                vm_manager=vm_manager,
                                node_info=node_info,
                                vm_config=self.vm_config)

        # close connection
        vm_manager.close()

        return status

    def boot(self):
        """
        boot vm
        :param :
        :return:
        :rtype:
        """
        # check running status
        running_status = self.vm_manager.check_running_state(domain=self.domain)
        if running_status:
            self.vm_obj.state = VM_RUNNING
            self.vm_obj.save()
            return True

        # boot
        status = self.vm_manager.start(domain=self.domain)
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
        # check running status
        running_status = self.vm_manager.check_running_state(domain=self.domain)
        if not running_status:
            self.vm_obj.state = VM_DESTROYED
            self.vm_obj.save()
            return True

        status = self.vm_manager.destroy(domain=self.domain)
        if status:
            self.vm_obj.state = VM_DESTROYED
            self.vm_obj.save()
            return True
        else:
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'vm shutdown failed'
            self.vm_obj.save()
            return False

    def reboot(self):
        """
        reboot vm
        :param :
        :return:
        :rtype:
        """
        # shutdown
        self.shutdown()

        # boot
        status = self.boot()

        return status

    def delete(self):
        """
        delete vm
        :param :
        :return:
        :rtype:
        """
        # shutdown vm
        self.shutdown()

        # undefine vm
        status = self.vm_manager.undefine(domain=self.domain)

        if not status:
            self.vm_obj.state = VM_FAILED
            self.vm_obj.note = 'vm undefine failed'
            self.vm_obj.save()
            return False

        # remove image
        status = utils.ssh_remove_file(ssh_host=self.node_info.get('host'),
                                       ssh_port=self.node_info.get('ssh_port'),
                                       ssh_user=self.node_info.get('ssh_user'),
                                       ssh_path=settings.SSH_PATH,
                                       file_to_remove=self.vm_obj.image_path)

        # remove vnc token
        vnc_token = self.vm_obj.vm_name
        status = NOVNC_MANAGER.remove_token(token=vnc_token)

        self.vm_obj.state = VM_DELETED
        self.vm_obj.save()

        return True

    def rebuild(self):
        """
        rebuild vm
        :param :
        :return:
        :rtype:
        """
        # delete old vm
        if self.domain:
            status = self.delete()

        # todo check vm reqirements
        # create vm
        vm_config = self.vm_obj.__dict__
        vm_config['base_image_path'] = self.vm_obj.template.image_path
        status = self.create_vm(vm_name=self.vm_obj.vm_name,
                                vm_manager=self.vm_manager,
                                node_info=self.node_info,
                                vm_config=vm_config)
        return status

    def __enter__(self):
        """
        connect to vm_manager and get domain
        :param :
        :return:
        :rtype:
        """
        if self.vm_config.get('action') == 'create':
            return self

        # connect to node
        self.vm_manager = self.connect_node(node_info=self.node_info)
        if not self.vm_manager:
            raise Exception

        # get domain
        self.domain = self.get_domain(vm_manager=self.vm_manager)
        if not self.domain and self.vm_config.get('action') != 'rebuild':
            raise Exception

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

