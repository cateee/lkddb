#: lkddb/linux/linux_kbuild.py : sources reader for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2010  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import fmt

class kver_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "kver")

    kind = ("linux-kernel", "special")

    cols = ((1, 'version', fmt.int, "INTEGER"),
	   (2, 'patchlevel', fmt.int, "INTEGER"),
	   (3, 'sublevel', fmt.int, "INTEGER"),
	   (4, 'extraversion', fmt.int, "INTEGER"),
	   (0, 'localversion', fmt.int, "INTEGER"),
           (0, 'ver_str', fmt.str, "TEXT"),
           (0, 'name', fmt.qstr, "TEXT"),
	   (-99, 'version', None, "$kver"))


class kconf_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "kconf")

    kind = ("linux-kernel", "special")

    cols = ((1, 'type', fmt.str, "TEXT"),
           (2, 'descr', fmt.str, "TEXT"),
           (0, 'depends', fmt.str, "TEXT"),
           (0, 'help', fmt.str, "TEXT"),
	   (-1, 'config', fmt.str, "TEXT"),
           (-2, 'filename', fmt.filename, "TEXT"),
           (-99, 'version', None, "$kver"))

    def get_lines(self):
        # we don't export lines for kconf: multiline data
        return []


class module_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "module")

    kind = ("linux-kernel", "device")

    cols = ((1, 'name', fmt.str, "TEXT"),
           (0, 'descr', fmt.qstr, "TEXT"),
           (-1, 'config',  fmt.str, "$config"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-99, 'version', None, "$kver"))


class firmware_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "firmware")

    kind = ("linux-kernel", "device")

    cols = ((-1, 'config',  fmt.str, "$config"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-99, 'version', None, "$kver"))


