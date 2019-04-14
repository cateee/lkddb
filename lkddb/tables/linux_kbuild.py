#!/usr/bin/python
#: lkddb/linux/linux_kbuild.py : tables for Linux kernel build infrastructure
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import lkddb
from lkddb import fmt
import lkddb.linux


@lkddb.register_to_group(lkddb.linux.tables)
class kver_table(lkddb.Table):

    def __init__(self):
        super().__init__("kver")
        self.kind = ("linux-kernel", "special")
        self.cols = ((1, 'version', fmt.int, "INTEGER"),
                     (2, 'patchlevel', fmt.int, "INTEGER"),
                     (3, 'sublevel', fmt.int, "INTEGER"),
                     (4, 'extraversion', fmt.int, "INTEGER"),
                     (0, 'localversion', fmt.int, "INTEGER"),
                     (0, 'ver_str', fmt.str, "TEXT"),
                     (0, 'name', fmt.qstr, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class kconf_table(lkddb.Table):

    def __init__(self):
        super().__init__("kconf")
        self.kind = ("linux-kernel", "special")
        self.cols = ((1, 'type', fmt.str, "TEXT"),
                     (2, 'descr', fmt.str, "TEXT"),
                     (0, 'depends', fmt.str, "TEXT"),
                     (0, 'help', fmt.str, "TEXT"),
                     (-1, 'config', fmt.str, "TEXT"),
                     (-2, 'filename', fmt.filename, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()

    def get_lines(self):
        # we don't export lines for kconf: multiline data
        return []


@lkddb.register_to_group(lkddb.linux.tables)
class module_table(lkddb.Table):

    def __init__(self):
        super().__init__("module")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.str, "TEXT"),
                     (0, 'descr', fmt.qstr, "TEXT"),
                     (-1, 'config', fmt.str, "$config"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class firmware_table(lkddb.Table):

    def __init__(self):
        super().__init__("firmware")
        self.kind = ("linux-kernel", "device")
        self.cols = ((-1, 'config', fmt.str, "$config"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()
