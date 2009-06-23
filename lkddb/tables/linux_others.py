#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb.fmt import *


class i2c_snd_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "i2c_snd_table")

    row_fmt = (fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("i2c_snd %s\t%s # %s\n")
    names = ('name', 'deps', 'filename')
    fmt_line = ('i2c_snd\t%(name)s' +
                '\t%(deps)s\t%(filename)s\n' )


class platform_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "platform_table")

    row_fmt = (fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("platform %s\t%s # %s\n")
    names = ('name', 'deps', 'filename')
    fmt_line = ('platform\t%(name)s' +
                '\t%(deps)s\t%(filename)s\n' )


class fs_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "fs_table")

    row_fmt = (fmt_qstr, 
                fmt_deps, fmt_filename)
    line_templ = ("fs %s\t%s # %s\n")
    names = ('name', 'deps', 'filename')
    fmt_line = ('fs\t%(name)s' +
                '\t%(deps)s\t%(filename)s\n' )


def register():
    lkddb.register_table('i2c_snd', i2c_snd_table())
    lkddb.register_table('platform', platform_table())
    lkddb.register_table('fs', fs_table())


