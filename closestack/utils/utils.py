#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-26 11:59
"""

import shlex
import subprocess

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
