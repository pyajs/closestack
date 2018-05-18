#!/usr/bin/env python
# -*- coding: utf-8 -*-
# custom configs

"""
@author:knktc
@contact:me@knktc.com
@create:2018-05-18 21:55
"""

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

