#!/usr/bin/env python
# -*- coding: utf-8 -*-
# views for create vm template

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-27 22:00
"""

import json
from ..utils import utils
from json.decoder import JSONDecodeError
from ..response import success, failed
from ..models import VmTemplate
from django.views import View
from django.conf import settings
from django.utils import timezone
from django.db import IntegrityError

__author__ = 'knktc'
__version__ = '0.1'

# config
SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "enable": {"type": "boolean"},
        "image_path": {"type": "string", "maxLength": 1024},
        "cpu": {"type": "integer", "minimum": 1},
        "memory": {"type": "integer", "minimum": 131072},
        "host_passthrough": {"type": "boolean"},
        "note": {"type": "string"}
    }
}


class VmTemplateListView(View):
    http_method_names = ['get', 'post']

    @staticmethod
    def post(request):
        """
        add a vm template
        :param :
        :return: creation result
        :rtype:
        """
        # load request json
        try:
            request_content = json.loads(request.body)
        except JSONDecodeError as e:
            return failed(status=1000001)

        # validate request data
        schema = SCHEMA.copy()
        schema['required'] = ['name', 'image_path']
        validate_result, msg = utils.validate_json(data=request_content, schema=schema)
        if validate_result != 0:
            return failed(status=1000001, msg=msg)

        # create new vm template
        new_obj = VmTemplate(
            name=request_content.get('name'),
            enable=request_content.get('enable', True),
            image_path=request_content.get('image_path'),
            config=request_content.get('config', settings.DEFAULT_VM_CONFIG),
            create_time=timezone.now(),
            note=request_content.get('note')
        )

        # save objects
        try:
            new_obj.save()
        except IntegrityError as e:
            return failed(status=1001001)

        # return data
        data = {
            'id': new_obj.id,
            'name': new_obj.name,
            'image_path': new_obj.image_path,
        }
        return success(data=data)

    @staticmethod
    def get(request):
        """
        get vm template list
        :param :
        :return: template list
        :rtype:
        """
        pass


class VmTemplateDetailView(View):
    http_method_names = ['get', 'post', 'patch', 'delete']


