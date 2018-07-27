#!/usr/bin/env python
# -*- coding: utf-8 -*-
# api to manage vms

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-01 22:08
"""

import json

from django.conf import settings
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from closestack.utils.node_utils import NodeManager
from closestack.response import success, failed
from closestack.utils import utils, spooler_utils
from closestack.models import VmRunning, VmTemplate
from closestack.utils.novnc_utils import NovncManager
from closestack.utils import vm_model_utils


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
    }
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


class VmManagerListView(View):
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
            'state': 0,
            'vm_id': vm_obj.id,
        })

        return success(data=result)


class VmManagerDetailView(View):
    http_method_names = ['get']

    @staticmethod
    def get(request, **kwargs):
        """
        get single vm detail by vm id
        :param :
        :return:
        :rtype:
        """
        # get vm object
        vm_id = kwargs.get('id')
        vm_obj = vm_model_utils.get_vm_obj(vm_id=vm_id)
        if not vm_obj:
            return failed(status=1002011)

        result = {
            'vm_id': vm_obj.id,
            'vm_name': vm_obj.vm_name,
            'name': vm_obj.name,
            'template': vm_obj.template_id,
            'state': vm_obj.state,
            'node': json.loads(vm_obj.node) if vm_obj.node is not None else None
        }

        return success(data=result)


class VmActionView(View):
    http_method_names = ['post']

    def boot(self, vm_obj):
        """ 
        boot vm
        :param :  
        :return:
        :rtype: 
        """
        task = {
            'action': 'boot',
            'vm_id': vm_obj.id,
        }

        # write task to spooler
        if spooler_utils.add_task(queue='boot', data=task):
            return 0, None
        else:
            return 1002016, None

    def post(self, request, **kwargs):
        """
        perform vm actions
        :param :
        :return:
        :rtype:
        """
        # validate request
        required_fields = ['action', ]
        request_content, msg = utils.validate_request(schema=ACTION_SCHEMA.copy(),
                                                      request=request,
                                                      required_fields=required_fields)
        if request_content is None:
            return failed(status=1000001, msg=msg)

        # validate vm id
        vm_id = kwargs.get('id')
        vm_obj = vm_model_utils.get_vm_obj(vm_id=vm_id)
        if not vm_obj:
            return failed(status=1002011)

        # run action
        action = request_content.get('action')

        status, data = getattr(self, action)(vm_obj)
        if status == 0:
            return success(data=data)
        else:
            return failed(status=status)
