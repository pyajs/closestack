![123](https://img.shields.io/badge/status-developing-yellow.svg) [![Build Status](https://travis-ci.org/pyajs/closestack.svg?branch=master)](https://travis-ci.org/pyajs/closestack)

# CLOSESTACK
`CloseStack` is a simple libvirt http wrapper. Written in Django.

## What it Does

`CloseStack` allows you to manage KVM vms by HTTP API. It is suitable for the following scenarios:

1. Single Host Machine
2. Multiple Host Machines, but you do not want to deploy OpenStack
3. Simple VM Lifecycle(create, destroy, undefine only)


## Requirements
* CentOS 7(other linux distros may work too)
* Python 3.6+
* Django 2.0+
* uwsgi 2.0
* jsonschema 2.6.0+
* libvirt-python 4.3.0+
* uhashring 1.1+

## Conception


## Installation


## Configuration


## Related Posts

* [Use uwsgi spooler as async queue(Chinese)](https://knktc.com/2018/07/24/uwsgi-spooler-as-async-queue/)
* [How to duplicate kvm snapshot(Chinese)](https://knktc.com/2018/06/12/how-to-duplicate-kvm-snapshot/)