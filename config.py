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

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# debug mode
DEBUG = True

# spooler dir
SPOOLER_DIR = os.path.join(SCRIPT_DIR, 'tasks')

# database config
# you can use sqlite3 as database, for debug and development only
DATABASE = {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(SCRIPT_DIR, 'db.sqlite3'),
}

# uncomment the following lines to use PostgreSQL as database server, recommanded for production deployment
'''
DATABASE = {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'db_name',
    'USER': 'db_user',
    'PASSWORD': 'db_password',
    'HOST': '127.0.0.1',
    'PORT': '5432'
}
'''

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

# SSH path
SSH_PATH = '/usr/bin/ssh'

# dir to store VM config xml templates
VM_TEMPLATE_DIR = os.path.join(SCRIPT_DIR, 'vm_templates')


# VM nodes
VM_NODES = {
    'node1': {
        # please make sure you've add ssh public key to the host
        'host': 'node1.myhost',
        'ssh_port': 22,
        'ssh_user': 'root',

        # we only tested qemu+ssh, and do not modify the tailing '/system'
        'conn': 'qemu+ssh://root@node1.myhost:22/system',

        # you can use the variables defined before
        'qemu_img_exec': QEMU_IMG_EXEC,
        'qemu_kvm_exec': QEMU_KVM_EXEC,

        # dir to store template images, should be a mounted NFS drive
        'image_dir': '/opt/closestack/images',

        # dir to store the running images, a SSD is recommended
        'running_image_dir': '/opt/closestack/running',

        # file name of vm template xml, you should put template xml into VM_TEMPLATE_DIR
        'vm_template': 'vm_template.xml'
    },
    # well, following is a complete node config, without comments
    'node2': {
        'host': 'node2.myhost',
        'ssh_port': 22,
        'ssh_user': 'root',
        'conn': 'qemu+ssh://root@node2.myhost:22/system',
        'qemu_img_exec': QEMU_IMG_EXEC,
        'qemu_kvm_exec': QEMU_KVM_EXEC,
        'image_dir': '/opt/closestack/images',
        'running_image_dir': '/opt/closestack/running',
        'vm_template': 'vm_template_for_fedora.xml'
    },

}


# default(or minimum requirements for a vm)
DEFAULT_VM_CONFIG = {
    "cpu": 1,  # cores of cpu
    "memory": 524288,  # memory(in KiB)
    "host_passthrough": False  # enable host passthrough
}

# NOVNC config
NOVNC_TOKEN_DIR = '/dir/to/novnc/tokens'
# novnc client in browser will use NOVNC_HOST, so you should use local machine's IP or hostname for this config
NOVNC_HOST = 'novnc.host'
NOVNC_PORT = 8787

