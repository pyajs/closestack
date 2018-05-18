#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vm node manager, use this module to choose a node to create vm

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-18 21:52
"""

from uhashring import HashRing

__author__ = 'knktc'
__version__ = '0.1'


class NodeManager(object):
    def __init__(self, nodes):
        """

        :param :
        :return:
        :rtype:
        """
        self.nodes = nodes
        self.hr = HashRing(nodes=nodes.keys(), hash_fn='ketama')

    def get_node(self, key):
        """
        get node by key, and return node config
        :param :
        :return:
        :rtype:
        """
        node_name = self.hr.get_node(key)
        return self.nodes.get(node_name)

    def add_node(self):
        """

        :param :
        :return:
        :rtype:
        """
        raise NotImplementedError

    def remove_node(self):
        """

        :param :
        :return:
        :rtype:
        """
        raise NotImplementedError


def main():
    """
    main process

    """


if __name__ == '__main__':
    main()