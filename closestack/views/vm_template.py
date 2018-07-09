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
from django.db import IntegrityError
from django.db.models import Q
import operator
from closestack.models import VmTemplate
from functools import reduce


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
        new_obj = VmTemplate(**request_content)

        # save objects
        try:
            new_obj.save()
        except IntegrityError as e:

            return failed(status=1001001, msg=str(e.__cause__))

        # return data
        data = new_obj.__dict__
        data.pop('_state')
        return success(data=data)

    @staticmethod
    def get(request):
        """
        get vm template list
        :param :
        :return: template list
        :rtype:
        """
        # order by fields
        order_by_fields = {'create_time', 'update_time', '-create_time', '-update_time'}

        # some query args
        limit = request.GET.get('limit', 10)
        offset = request.GET.get('offset', 0)
        order_by = request.GET.get('orderby', '-update_time')
        enable = request.GET.get('enable')

        # format query
        query_args = {}

        # check orderby field
        if order_by not in order_by_fields:
            order_by = '-update_time'

        # filter with enable field
        if not enable:
            pass
        else:
            enable = str(enable).lower()
            if enable == 'true':
                query_args['enable'] = True
            elif enable == 'false':
                query_args['enable'] = False
            else:
                pass

        # get limit and offset, for pagination
        try:
            limit = int(limit)
        except Exception as e:
            limit = 10

        try:
            offset = int(offset)
        except Exception as e:
            offset = 0

        # query
        query_set = VmTemplate.objects.filter(**query_args).order_by(order_by)
        total = query_set.count()
        query_set_values = query_set[offset: offset + limit].values()
        templates = []
        for single_query_set in query_set_values:
            templates.append(single_query_set)

        result = {
            'total': total,
            'templates': templates
        }

        return success(data=result)


class VmTemplateDetailView(View):
    http_method_names = ['get', 'post', 'patch', 'delete']


