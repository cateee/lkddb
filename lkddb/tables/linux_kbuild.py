#: lkddb/linux/version.py : sources reader for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import fmt

class kver_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "kver_table")

    names = ('version', 'ver_str', 'is_a_release', 'name')
    row_fmt = (fmt.m32x, fmt.str, fmt.int, fmt.qstr)
    line_templ = ("kver %s %s %s %s\n")


class kconf_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "kconf_table")

    names = ('config', 'filename', 'type', 'descr', 'depends', 'help')

    def add_row_fmt(self, row):
	pass

    def get_lines(self):
        # we don't export lines for kconf: multiline data
        return []


class module_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "module_table")

    names = ('name', 'descr', 'config', 'filename')
    row_fmt = (fmt.str, fmt.qstr, fmt.str, fmt.filename)
    line_templ = ("module %s %s\t%s\t%s\n")

class firmware_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "firmware_table")

    names = ('config', 'filename')
    row_fmt = (fmt.str, fmt.filename)
    line_templ = ("firmware %s\t%s\n")

