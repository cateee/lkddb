#!/usr/bin/python
#: lkddb/tables/ids_tables.py : tables for ids files
#
#  Copyright (c) 2000,2001,2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import lkddb
from lkddb import fmt

class pci_ids_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pci_ids")

    kind = ("ids", "ids")

    cols = ((1, 'vendor', fmt.m16x, "INTEGER"),
           (2, 'device', fmt.m16x, "INTEGER"),
           (3, 'subvendor', fmt.m16x, "INTEGER"),
           (4, 'subdevice', fmt.m16x, "INTEGER"),
           (0, 'name', fmt.str, "TEXT"),
           (-99, 'version', None, "$kver"))


class pci_class_ids_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pci_class_ids")

    kind = ("ids", "ids")

    cols = ((1, 'class', fmt.m8x, "INTEGER"),
           (2, 'subclass', fmt.m8x, "INTEGER"),
           (3, 'prog-inf', fmt.m8x, "INTEGER"),
           (0, 'name', fmt.str, "TEXT"),
           (-99, 'version', None, "$kver"))


class usb_ids_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "usb_ids")

    kind = ("ids", "ids")

    cols = ((1, 'vendor_id', fmt.m16x, "INTEGER"),
           (2, 'model_id', fmt.m16x, "INTEGER"),
           (0, 'name', fmt.str, "TEXT"),
           (-99, 'version', None, "$kver"))


class usb_class_ids_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "usb_class_ids")

    kind = ("ids", "ids")

    cols = ((1, 'class', fmt.m8x, "INTEGER"),
           (2, 'subclass', fmt.m8x, "INTEGER"),
           (3, 'protocol', fmt.m8x, "INTEGER"),
           (0, 'name', fmt.str, "TEXT"),
           (-99, 'version', None, "$kver"))


class eisa_ids_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "eisa_ids")

    kind = ("ids", "ids")

    cols = ((1, 'id', fmt.dqstr, "TEXT"),
           (0, 'name', fmt.dqstr, "TEXT"),
           (-99, 'version', None, "$kver"))


class zorro_ids_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "zorro_ids")

    kind = ("ids", "ids")

    cols = ((1, 'manufacter', fmt.m16x, "INTEGER"),
           (2, 'product', fmt.m16x, "INTEGER"),
           (0, 'name', fmt.str, "TEXT"),
           (-99, 'version', None, "$kver"))


