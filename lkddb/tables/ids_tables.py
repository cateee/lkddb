#!/usr/bin/python
#: lkddb/tables/ids_tables.py : tables for ids files
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import lkddb
from lkddb import fmt
import lkddb.ids


@lkddb.register_to_group(lkddb.ids.tables)
class pci_ids_table(lkddb.Table):

    def __init__(self):
        super().__init__("pci_ids")
        self.kind = ("ids", "ids")
        self.cols = ((1, 'vendor', fmt.m16x, "INTEGER"),
                     (2, 'device', fmt.m16x, "INTEGER"),
                     (3, 'subvendor', fmt.m16x, "INTEGER"),
                     (4, 'subdevice', fmt.m16x, "INTEGER"),
                     (0, 'name', fmt.str, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.ids.tables)
class pci_class_ids_table(lkddb.Table):

    def __init__(self):
        super().__init__("pci_class_ids")
        self.kind = ("ids", "ids")
        self.cols = ((1, 'class', fmt.m8x, "INTEGER"),
                     (2, 'subclass', fmt.m8x, "INTEGER"),
                     (3, 'prog-inf', fmt.m8x, "INTEGER"),
                     (0, 'name', fmt.str, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.ids.tables)
class usb_ids_table(lkddb.Table):

    def __init__(self):
        super().__init__("usb_ids")
        self.kind = ("ids", "ids")
        self.cols = ((1, 'vendor_id', fmt.m16x, "INTEGER"),
                     (2, 'model_id', fmt.m16x, "INTEGER"),
                     (0, 'name', fmt.str, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.ids.tables)
class usb_class_ids_table(lkddb.Table):

    def __init__(self):
        super().__init__("usb_class_ids")
        self.kind = ("ids", "ids")
        self.cols = ((1, 'class', fmt.m8x, "INTEGER"),
                     (2, 'subclass', fmt.m8x, "INTEGER"),
                     (3, 'protocol', fmt.m8x, "INTEGER"),
                     (0, 'name', fmt.str, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.ids.tables)
class eisa_ids_table(lkddb.Table):

    def __init__(self):
        super().__init__("eisa_ids")
        self.kind = ("ids", "ids")
        self.cols = ((1, 'id', fmt.dqstr, "TEXT"),
                     (0, 'name', fmt.dqstr, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.ids.tables)
class zorro_ids_table(lkddb.Table):

    def __init__(self):
        super().__init__("zorro_ids")
        self.kind = ("ids", "ids")
        self.cols = ((1, 'manufacter', fmt.m16x, "INTEGER"),
                     (2, 'product', fmt.m16x, "INTEGER"),
                     (0, 'name', fmt.str, "TEXT"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()
