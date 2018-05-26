#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-18 22:55
"""

import os
import uuid

__author__ = 'knktc'
__version__ = '0.1'


class NovncManager(object):
    def __init__(self, token_dir):
        """
        init
        :param token_dir: where to store token file
        :return:
        :rtype:
        """
        self.token_dir = token_dir

    def add_token(self, host, vnc_port, permanent=False):
        """
        add token file
        :param host: vnc host
        :param vnc_port: vnc port
        :param permanent: if not permanent, the token file may be cleaned by a contab task
        :return: create result or
        :rtype: tuple
        """
        token = str(uuid.uuid4())
        if permanent:
            prefix = 'permanent_'
        else:
            prefix = ''
        token_filename = '{}{}.token'.format(prefix, token)
        config_string = '{}: {}:{}'.format(token, host, vnc_port)

        # write token
        token_filepath = os.path.join(self.token_dir, token_filename)
        try:
            with open(token_filepath, 'w') as f:
                f.write(config_string)
            result = {
                'token': token,
                'host': host,
                'vnc_port': vnc_port,
                'permanent': permanent
            }
            return True, result
        except:
            return False, None

    def remove_token(self, token, permanent=False):
        """
        remove token file
        :param token: token, the uuid
        :return: remove result
        :rtype: bool
        """
        if permanent:
            prefix = 'permanent_'
        else:
            prefix = ''

        token_filename = '{}{}.token'.format(prefix, token)
        token_filepath = os.path.join(self.token_dir, token_filename)
        if os.path.isfile(token_filepath):
            try:
                os.remove(token_filepath)
                return True
            except:
                return False
        else:
            return False


def main():
    """
    main process

    """


if __name__ == '__main__':
    main()