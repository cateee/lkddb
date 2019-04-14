#!/usr/bin/python
#: lkddb/tables/linux_others.py : tables for miscelaneous Linux kernel structures
#
#  Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import lkddb
from lkddb import fmt
import lkddb.linux

@lkddb.register_to_group(lkddb.linux.tables)
class i2c_snd_table(lkddb.Table):

    def __init__(self):
        super().__init__("i2c-snd")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class platform_table(lkddb.Table):

    def __init__(self):
        super().__init__("platform")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class fs_table(lkddb.Table):

    def __init__(self):
        super().__init__("fs")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()
