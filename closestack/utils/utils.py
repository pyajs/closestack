#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-26 11:59
"""

import json
import shlex
import subprocess
from json.decoder import JSONDecodeError
from string import Template

from django.core.exceptions import ObjectDoesNotExist
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

from closestack.models import VmTemplate

__author__ = 'knktc'
__version__ = '0.1'


def cmd_runner(cmd, timeout=60):
    """ 
    a command runner with timeout

    :param timeout: timeout in seconds, default 60s
    :param cmd: command
    :return: a tuple, contains command status, output, and command returncode(return by the command, for debug)
    :rtype: tuple

    status
    ======
    0: success
    1: command timeout
    2: command execute failed, you should check the output and returncode for debug
    """
    try:
        output = subprocess.check_output(shlex.split(cmd), timeout=timeout, stderr=subprocess.STDOUT)
        return 0, output, 0
    except subprocess.TimeoutExpired:
        return 1, 'command timeout', None
    except subprocess.CalledProcessError as e:
        return 2, e.output, e.returncode


def validate_json(data, schema):
    """
    use jsonschema to validate input data

    :param data: data to be validated
    :param schema: json schema
    :return: validate result as status code and error message
    :rtype: tuple

    status
    ========
    0: success
    1: data validate failed
    2: schema validate failed
    3: other error
    """
    try:
        validate(data, schema)
        return 0, None
    except ValidationError as e:
        return 1, "data error on field '{}': {}".format('.'.join(str(x) for x in e.path), e.message)
    except SchemaError as e:
        return 2, "schema error on field '{}': {}".format('.'.join(str(x) for x in e.path), e.message)


def format_vm_xml(template, config_dict):
    """
    format vm xml with template and vm config dict
    :param config_dict: config dict, contains cpus, ram and other configs
    :param template: template content
    :return: formated xml
    :rtype: str
    """
    try:
        formated_xml = Template(template).substitute(config_dict)
        return formated_xml
    except Exception as e:
        return None


def validate_vm_config(vm_config):
    """
    valiate vm config, return validation result and vm config
    :param vm_config: raw vm config dict
    :return: validation result and vm config
    :rtype: tuple

    # status
    =========
    0: success
    1: template ID not exists
    2: cpu does not reach minimum requirements
    3: memory doest not reach minimum requirements
    4: host_passthrough config needed
    5: vm name duplicated

    """
    # check template id
    template_id = vm_config.get('template_id')
    try:
        template_obj = VmTemplate.objects.get(id=template_id)
        vm_config['base_image_path'] = template_obj.image_path
    except ObjectDoesNotExist:
        return 1, None

    # validate minimum vm config
    # cpu
    cpu = vm_config.get('cpu')
    if cpu is None:
        vm_config['cpu'] = template_obj.cpu
    elif cpu < template_obj.cpu:
        return 2, None

    # memory
    memory = vm_config.get('memory')
    if memory is None:
        vm_config['memory'] = template_obj.memory
    elif memory < template_obj.memory:
        return 3, None

    # host_passthrough
    host_passthrough = vm_config.get('host_passthrough')
    if host_passthrough is None:
        vm_config['host_passthrough'] = template_obj.host_passthrough
    elif template_obj.host_passthrough and not host_passthrough:
        return 4, None

    # other params
    vm_config.setdefault('persistent', True)
    vm_config.setdefault('auto_start', True)

    return 0, vm_config


def ssh_remove_file(ssh_host, ssh_user, file_to_remove, ssh_port=22, ssh_path='/usr/bin/ssh'):
    """
    use ssh to remove remote file
    :param ssh_path: ssh command path, default /usr/bin/ssh
    :param file_to_remove: the file path
    :param ssh_user: ssh user, make sure you have permission to remove the file
    :param ssh_port: ssh port, default 22
    :param ssh_host: ssh host
    :return: remove result
    :rtype: bool
    """
    cmd = "{} -p {} {}@{} rm -f '{}'".format(ssh_path, ssh_port, ssh_user, ssh_host, file_to_remove)
    code, stdout, stderr = cmd_runner(cmd=cmd)
    if code == 0:
        return True
    else:
        return False


def validate_request(request, schema, required_fields):
    """
    validate request
    :param required_fields: required fields as a list
    :param schema: jsonschema
    :param request: http request object
    :return: json loaded request body and error message
    :rtype: tuple
    """
    # load request json
    try:
        request_content = json.loads(request.body)
    except JSONDecodeError as e:
        return None, 'json data decord failed'

    # validate request data with jsonschema
    schema['required'] = required_fields
    validate_result, msg = validate_json(data=request_content, schema=schema)
    if validate_result != 0:
        return None, msg

    return request_content, None
