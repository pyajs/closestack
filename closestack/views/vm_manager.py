#!/usr/bin/env python
# -*- coding: utf-8 -*-
# api to manage vms

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-01 22:08
"""

import json

from django.views import View
from closestack.response import success, failed
from closestack.utils import utils, spooler_utils
from closestack.models import VmRunning
from closestack.utils import vm_model_utils, remote_console_utils


__author__ = 'knktc'
__version__ = '0.1'


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

REMOTE_CONSOLE_SCHEMA = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ['novnc']}
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
            'node': json.loads(vm_obj.node) if vm_obj.node is not None else None,
            'note': vm_obj.note,
        }

        return success(data=result)


class VmActionView(View):
    http_method_names = ['post']

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
        if not vm_model_utils.get_vm_obj(vm_id=vm_id):
            return failed(status=1002011)

        # run action
        action = request_content.get('action')

        task = {
            'action': action,
            'vm_id': vm_id,
        }

        # write task to spooler
        if spooler_utils.add_task(queue=action, data=task):
            return success()
        else:
            return failed(status=1002015)


class VmRemoteConsoleView(View):
    http_method_names = ['post']

    def post(self, request, **kwargs):
        """
        get remote console, eg. novnc
        :param :
        :return:
        :rtype:
        """
        # validate request
        required_fields = ['type', ]
        request_content, msg = utils.validate_request(schema=REMOTE_CONSOLE_SCHEMA.copy(),
                                                      request=request,
                                                      required_fields=required_fields)
        if request_content is None:
            return failed(status=1000001, msg=msg)

        # vlidate vm id
        vm_id = kwargs.get('id')
        vm_obj = vm_model_utils.get_vm_obj(vm_id=vm_id)
        if not vm_obj:
            return failed(status=1002011)

        remote_console_type = request_content.get('type')
        # get remote console
        try:
            with remote_console_utils.RemoteConsole(vm_obj=vm_obj) as remote_console:
                result = getattr(remote_console, remote_console_type)()
        except remote_console_utils.RemoteConsoleError as e:
            return failed(status=1002016, msg=e.value)

        return success(data=result)

