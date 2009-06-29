#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb.linux.scanners import *
from .browse_sources import struct_parent_scanner, parse_struct


# device_driver include/linux/device.h
device_driver_fields = (
    "name", "bus", "kobj", "klist_devices", "knode_bus", "owner", "mod_name",
    "mkobj", "probe", "remove", "shutdown", "suspend", "resume")


# I2C snd , snd_i2c_device_create sound/i2c/i2c.c

class i2c_snd(function_scanner):

    def __init__(self, parent_scanner):
      function_scanner.__init__(self,
          name = 'i2c_snd',
          table_name = 'i2c-snd',
          parent_scanner = parent_scanner,
          funct_name = "snd_i2c_device_create",
          funct_fields = ("bus", "name", "addr", "rdevice")
          )

    def store(self, dict):
        v0 = extract_string("name", dict)
        if v0 == "":
            return None
        return (v0,)

# "platform" , platform_driver include/linux/platform_device.h

class platform(struct_scanner):

    def __init__(self, parent_scanner):
      struct_scanner.__init__(self,
          name = 'platform',
          table_name = 'platform',
          parent_scanner = parent_scanner,
          struct_name = "platform_driver",
          struct_fields = ("probe", "remove", "shutdown", "suspend_late", "resume_early",
			   "suspend", "resume", "driver")
          )

    def store(self, dict):
	block = dict.get("driver", None)
        if not block:
            return None
        line = split_structs(block)[0]
        driver_dict = parse_struct(None, device_driver_fields, line, None, None, ret=True)
        v0 = extract_string("name", driver_dict)
        return (v0,)


# fs , file_system_type include/linux/fs.h

class fs(struct_scanner):

    def __init__(self, parent_scanner):
      struct_scanner.__init__(self,
          name = 'fs',
          table_name = 'fs',
          parent_scanner = parent_scanner,
          struct_name = "file_system_type",
          struct_fields = ("name", "fs_flags", "get_sb", "kill_sb", "owner",
		"next", "fs_supers", "s_lock_key", "s_umount_key", "i_lock_key", "i_mutex_key",
		"i_mutex_dir_key", "i_alloc_sem_key")
          )

    def store(self, dict):
	v0 = extract_string("name", dict)
        return (v0,)

