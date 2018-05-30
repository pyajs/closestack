#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-26 11:59
"""

import shlex
import subprocess
from jsonschema import validate
from jsonschema.exceptions import ValidationError, SchemaError

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
