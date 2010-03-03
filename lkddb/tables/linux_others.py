#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import fmt


class i2c_snd_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "i2c-snd", tree)

    cols = (('name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class platform_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "platform", tree)

    cols = (('name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class fs_table(lkddb.table, tree):

    def __init__(self):
        lkddb.table.__init__(self, "fs", tree)

    cols = (('name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


def register(tree):
    lkddb.register_table('i2c-snd', i2c_snd_table(tree))
    lkddb.register_table('platform', platform_table(tree))
    lkddb.register_table('fs', fs_table(tree))


