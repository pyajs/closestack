#!/usr/bin/env python
# -*- coding: utf-8 -*-
# custom configs

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-18 21:55
"""

import os

__author__ = 'knktc'
__version__ = '0.1'

# QEMU commands
'''
QEMU commands config notes:

for centos7, use settings below:
QEMU_IMG_EXEC = '/usr/bin/qemu-img'
QEMU_KVM_EXEC = '/usr/libexec/qemu-kvm'

for fedora, you can use the following settings
QEMU_IMG_EXEC = '/bin/qemu-img'
QEMU_KVM_EXEC = '/bin/qemu-kvm'

for ubuntu, please help us to figure out the settings
'''
QEMU_IMG_EXEC = '/usr/bin/qemu-img'
QEMU_KVM_EXEC = '/usr/libexec/qemu-kvm'

# VM nodes
VM_NODES = {
    'node1': {
        # please make sure you've add ssh public key to the host
        'host': 'node1.myhost',
        'ssh_port': '22',
        'ssh_user': 'root',

        # we only tested qemu+ssh, and do not modify the tailing '/system'
        'conn': 'qemu+ssh://root@node1.myhost:22/system',

        # you can use the variables defined before
        'qemu_img_exec': QEMU_IMG_EXEC,
        'qemu_kvm_exec': QEMU_KVM_EXEC,

        # dir to store the running images, a SSD is recommended
        'running_image_dir': '/opt/closestack/running',
    },
    # well, following is a complete node config, without comments
    'node2': {
        'host': 'node2.myhost',
        'ssh_port': '22',
        'ssh_user': 'root',
        'conn': 'qemu+ssh://root@node2.myhost:22/system',
        'qemu_img_exec': QEMU_IMG_EXEC,
        'qemu_kvm_exec': QEMU_KVM_EXEC,
        'running_image_dir': '/opt/closestack/running',
    },

}

