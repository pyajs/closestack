#!/usr/bin/env python
# -*- coding: utf-8 -*-
# api to manage vms

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-01 22:08
"""

import os
import json
import uuid
from json.decoder import JSONDecodeError

from django.conf import settings
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from closestack.utils.node_utils import NodeManager
from closestack.response import success, failed
from closestack.utils import utils, spooler_utils
from closestack.models import VmRunning, VmTemplate
from closestack.utils.vm_utils import VmManager, VmManagerError
from closestack.utils.novnc_utils import NovncManager


__author__ = 'knktc'
__version__ = '0.1'


NODE_MANAGER = NodeManager(nodes=settings.VM_NODES)
NOVNC_MANAGER = NovncManager(token_dir=settings.NOVNC_TOKEN_DIR)


# schema
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "template_id": {"type": "integer"},
        "cpu": {"type": "integer", "minimum": 1},
        "memory": {"type": "integer", "minimum": 131072},
        "host_passthrough": {"type": "boolean"},
        "persistent": {"type": "boolean"},
        "auto_start": {"type": "boolean"},
        "note": {"type": "string"}
    }
}

AVAILABLE_ACTIONS = ['rebuild', 'boot', 'reboot', 'shutdown', 'delete']
ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "action": {"type": "string", "enum": AVAILABLE_ACTIONS}
    },
    "required": ["action"]
}

# errors
CONFIG_VALIDATE_ERRORS = {
    1: 1002001,
    2: 1002002,
    3: 1002003,
    4: 1002004,
}
VM_DEFINE_ERRORS = {
    1: 1002008,
    2: 1002009,
    3: 1002010,
}


class VmManagerView(View):
    http_method_names = ['get', 'post']

    @staticmethod
    def post(request):
        """
        create vm with template
        :param :
        :return:
        :rtype:
        """
        # validate request
        required_fields = ['name', 'template_id', ]
        request_content, msg = utils.validate_request(schema=SCHEMA.copy(),
                                                      request=request,
                                                      required_fields=required_fields)
        if request_content is None:
            return failed(status=1000001, msg=msg)

        # validate vm config
        validate_result, vm_config = utils.validate_vm_config(vm_config=request_content)

        if validate_result == 0:
            pass
        else:
            return failed(status=CONFIG_VALIDATE_ERRORS.get(validate_result))

        # form a task
        task = vm_config.copy()

        # write vm running info with pending state
        vm_config.pop('auto_start')
        vm_config.pop('base_image_path')
        vm_obj = VmRunning(**vm_config)
        vm_obj.save()

        task.update({
            'action': 'create',
            'vm_id': vm_obj.id,
        })

        # write task to spooler
        if spooler_utils.add_task(queue='create', data=task):
            pass
        else:
            return failed(status=1002015)

        result = vm_config.copy()
        result.update({
            'state': 0
        })

        return success(data=result)


class VmActionView(View):
    http_method_names = ['get', 'post']

    def get_vm_obj(self, vm_id):
        """
        get vm info by vm_id
        :param :
        :return:
        :rtype:
        """
        try:
            vm_obj = VmRunning.objects.get(id=vm_id)
            return vm_obj
        except ObjectDoesNotExist:
            return None

    def get_vm_manager(self, node_info):
        """
        get vm manager object
        :param node_info: node info
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

    def boot(self, vm_manager, domain, **kwargs):
        """ 
        boot vm
        :param :  
        :return:
        :rtype: 
        """
        status = vm_manager.start(domain=domain)
        if status:
            return 0
        else:
            return 1002013

    def shutdown(self, vm_manager, domain, **kwargs):
        """
        shutdown vm

        :param :
        :return:
        :rtype:
        """
        status = vm_manager.destroy(domain=domain)
        if status:
            return 0
        else:
            return 1002014

        
    def disconnect(self, vm_manager):
        """ 
        close connection to vm manager

        :param :  
        :return:
        :rtype: 
        """
        vm_manager.close()


    def post(self, request, **kwargs):
        """
        perform vm actions
        :param :
        :return:
        :rtype:
        """
        # get vm id
        vm_id = kwargs.get('id')

        # load request json
        try:
            request_content = json.loads(request.body)
        except JSONDecodeError as e:
            return failed(status=1000001)

        # validate request data
        schema = ACTION_SCHEMA.copy()
        validate_result, msg = utils.validate_json(data=request_content, schema=schema)
        if validate_result != 0:
            return failed(status=1000001, msg=msg)

        # check vm_id
        vm_obj = self.get_vm_obj(vm_id=vm_id)
        if not vm_obj:
            return failed(status=1002011)

        # get vm manager
        vm_manager = self.get_vm_manager(json.loads(vm_obj.node))
        if not vm_manager:
            return failed(status=1002006)

        # get domain
        vm_name = vm_obj.vm_name

        domain = vm_manager.get_domain_obj(vm_name=vm_name)
        if not domain:
            return 1002012

        # get action
        action = request_content.get('action')
        status = getattr(self, action)(vm_manager, domain)


        # disconnect vm manager
        self.disconnect(vm_manager=vm_manager)


        if status == 0:
            return success(data={'1': 2})
        else:
            return failed(status=status)


