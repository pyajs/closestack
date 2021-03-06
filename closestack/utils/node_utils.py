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
        init
        :param :
        :return:
        :rtype:
        """
        self.nodes = nodes
        self.hr = HashRing(nodes=nodes, hash_fn='ketama')

    def get_node(self, key):
        """
        get node by key, and return node config
        :param :
        :return:
        :rtype:
        """
        node_name = self.hr.get_node(key)
        node_info = self.nodes.get(node_name)
        node_info['name'] = node_name
        return node_info

    def add_node(self):
        """
        add node, not implemented yet
        :param :
        :return:
        :rtype:
        """
        raise NotImplementedError

    def remove_node(self):
        """
        remove node, not implemented yet
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
