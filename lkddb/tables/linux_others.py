#!/usr/bin/python
#: lkddb/tables/linux_others.py : tables for miscelaneous Linux kernel structures
#
#  Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import lkddb
from lkddb import fmt


class i2c_snd_table(lkddb.table):

    def __init__(self):
        super().__init__("i2c-snd")

    kind = ("linux-kernel", "device")

    cols = ((1, 'name', fmt.qstr, "TEXT"),
            (-1, 'deps', fmt.deps, "$deps"),
            (-2, 'filename', fmt.filename, "$filename"),
            (-99, 'version', None, "$kver"))


class platform_table(lkddb.table):

    def __init__(self):
        super().__init__("platform")

    kind = ("linux-kernel", "device")

    cols = ((1, 'name', fmt.qstr, "TEXT"),
            (-1, 'deps', fmt.deps, "$deps"),
            (-2, 'filename', fmt.filename, "$filename"),
            (-99, 'version', None, "$kver"))


class fs_table(lkddb.table):

    def __init__(self):
        super().__init__("fs")

    kind = ("linux-kernel", "device")

    cols = ((1, 'name', fmt.qstr, "TEXT"),
            (-1, 'deps', fmt.deps, "$deps"),
            (-2, 'filename', fmt.filename, "$filename"),
            (-99, 'version', None, "$kver"))


def register(tree):
    tree.register_table('i2c-snd', i2c_snd_table())
    tree.register_table('platform', platform_table())
    tree.register_table('fs', fs_table())
