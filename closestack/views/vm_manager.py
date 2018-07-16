#!/usr/bin/env python
# -*- coding: utf-8 -*-
# api to manage vms

"""
@author:knktc
@contact:me@knktc.com
@create:2018-07-01 22:08
"""

import json
from json.decoder import JSONDecodeError

from django.conf import settings
from django.views import View
from ..utils.node_utils import NodeManager
from ..response import success, failed
from ..utils import utils


__author__ = 'knktc'
__version__ = '0.1'


NODE_MANAGER = NodeManager(nodes=settings.VM_NODES)
# schema
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "template": {"type": "integer"},
        "cpu": {"type": "integer", "minimum": 1},
        "memory": {"type": "integer", "minimum": 131072},
        "host_passthrough": {"type": "boolean"},
        "persistent": {"type": "boolean"},
        "auto_start": {"type": "boolean"},
        "note": {"type": "string"}
    }
}

# errors
CONFIG_VALIDATE_ERRORS = {
    1: 1002001,
    2: 1002002,
    3: 1002003,
    4: 1002004,
    5: 1002005,
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

        # load request json
        try:
            request_content = json.loads(request.body)
        except JSONDecodeError as e:
            return failed(status=1000001)

        # validate request data
        schema = SCHEMA.copy()
        schema['required'] = ['name', 'template', ]
        validate_result, msg = utils.validate_json(data=request_content, schema=schema)
        if validate_result != 0:
            return failed(status=1000001, msg=msg)

        # validate vm config
        validate_result, vm_config = utils.validate_vm_config(vm_config=request_content)

        if validate_result == 0:
            pass
        else:
            return failed(status=CONFIG_VALIDATE_ERRORS.get(validate_result))

        # create vm



        return success(data=vm_config)








