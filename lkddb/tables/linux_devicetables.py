#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import fmt

class pci_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pci")

    kind = ("linux-kernel", "device")

    cols = ((1, 'vendor', fmt.m16x, "INTEGER"),
	   (2, 'device', fmt.m16x, "INTEGER"),
	   (3, 'subvendor', fmt.m16x, "INTEGER"),
	   (4, 'subdevice', fmt.m16x, "INTEGER"),
	   (0, 'class', None, "INTEGER"),
           (5, 'class_mask', fmt.special, "INTEGER"),
	   (-1, 'deps', fmt.deps, "$deps"),
	   (-2, 'filename', fmt.filename, "$filename"),
	   (-3, 'version', None, "$kver"))

    def add_row_fmt(self, row):
	m = fmt.mask_24m(fmt.m24x(row[4]), fmt.m24x(row[5]))
        lkddb.table.add_row_fmt(self, row[:4] + (m,) + row[6:])


class usb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "usb")

    kind = ("linux-kernel", "device")

    cols = ((1, 'idVendor', fmt.m16x, "INTEGER"),
	   (2, 'idProduct', fmt.m16x, "INTEGER"),
           (3, 'bDeviceClass', fmt.m8x, "INTEGER"),
	   (4, 'bDeviceSubClass', fmt.m8x, "INTEGER"),
	   (5, 'bDeviceProtocol', fmt.m8x, "INTEGER"),
           (6, 'bInterfaceClass', fmt.m8x, "INTEGER"),
	   (7, 'bInterfaceSubClass', fmt.m8x, "INTEGER"),
	   (8, 'bInterfaceProtocol', fmt.m8x, "INTEGER"),
           (0, 'bcdDevice_lo', fmt.m16x, "INTEGER"),
	   (0, 'bcdDevice_hi', fmt.m16x, "INTEGER"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class ieee1394_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ieee1394")

    kind = ("linux-kernel", "device")

    cols = ((1, 'vendor_id', fmt.m24x, "INTEGER"),
	   (2, 'model_id', fmt.m24x, "INTEGER"),
	   (3, 'specifier_id', fmt.m24x, "INTEGER"),
	   (4, 'version', fmt.m24x, "INTEGER"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class hid_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "hid")

    kind = ("linux-kernel", "device")

    cols = ((1, 'bus', fmt.m16x, "INTEGER"),
	   (2, 'vendor', fmt.m32x, "INTEGER"),
	   (3, 'product', fmt.m32x, "INTEGER"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class ccw_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ccw")

    kind = ("linux-kernel", "device")

    cols = ((1, 'cu_type', fmt.m16x, "INTEGER"),
	   (2, 'cu_model', fmt.m8x, "INTEGER"),
	   (3, 'dev_type', fmt.m16x, "INTEGER"),
	   (4, 'dev_model', fmt.m8x, "INTEGER"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


# s390 AP bus
class ap_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ap")

    kind = ("linux-kernel", "device")

    cols = ((1, 'dev_type', fmt.m8x, "INTEGER"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class acpi_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "acpi")

    kind = ("linux-kernel", "device")

    cols = ((1, 'id', fmt.qstr, "TEXT"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class pnp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pnp")

    kind = ("linux-kernel", "device")

    cols = ((1, 'id', fmt.qstr, "TEXT"),
	   (0, 'n0', fmt.qstr, "TEXT"),
	   (0, 'n1', fmt.qstr, "TEXT"),
	   (0, 'n2', fmt.qstr, "TEXT"),
	   (0, 'n3', fmt.qstr, "TEXT"),
	   (0, 'n4', fmt.qstr, "TEXT"),
	   (0, 'n5', fmt.qstr, "TEXT"),
	   (0, 'n6', fmt.qstr, "TEXT"),
	   (0, 'n7', fmt.qstr, "TEXT"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class serio_table(lkddb.table):

    kind = ("linux-kernel", "device")

    def __init__(self):
        lkddb.table.__init__(self, "serio")

    cols = ((1, 'type', fmt.m8x, "INTEGER"),
           (2, 'proto', fmt.m8x, "INTEGER"),
           (3, 'id', fmt.m8x, "INTEGER"),
           (4, 'extra', fmt.m8x, "INTEGER"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class of_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "of")

    kind = ("linux-kernel", "device")

    cols = ((1, 'name', fmt.qstr, "TEXT"),
	   (0, 'type', fmt.qstr, "TEXT"),
	   (0, 'compatible', fmt.qstr, "TEXT"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class vio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "vio")

    kind = ("linux-kernel", "device")

    cols = ((1, 'type', fmt.qstr, "TEXT"),
           (0, 'compat', fmt.qstr, "TEXT"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class pcmcia_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pcmcia")

    kind = ("linux-kernel", "device")

    cols = ((1, 'manf_id', fmt.m16x, "INTEGER"),
           (2, 'card_id', fmt.m16x, "INTEGER"),
           (3, 'func_id', fmt.m8x, "INTEGER"),
           (4, 'function', fmt.m8x, "INTEGER"),
           (5, 'device_no', fmt.m8x, "INTEGER"),
           (0, 'n0', fmt.qstr, "TEXT"),
           (0, 'n1', fmt.qstr, "TEXT"),
           (0, 'n2', fmt.qstr, "TEXT"),
           (0, 'n3', fmt.qstr, "TEXT"),
           (-1, 'deps', fmt.deps, "$deps"),
           (-2, 'filename', fmt.filename, "$filename"),
           (-3, 'version', None, "$kver"))


class input_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "input")

    kind = ("linux-kernel", "device")

    cols = (('bustype', fmt.m16x, "INTEGER"),
           ('vendor', fmt.m16x, "INTEGER"),
           ('product', fmt.m16x, "INTEGER"),
           ('version', fmt.m16x, "INTEGER"),
           ('evbit', fmt.m32x, "INTEGER"),    # 0x1f
           ('keybit', fmt.m32x, "INTEGER"),   # 0x71
           ('relbit', fmt.m32x, "INTEGER"),   # 0x2ff
           ('absbit', fmt.m16x, "INTEGER"),   # 0x0f
           ('mscbit', fmt.m32x, "INTEGER"),   # 0x3f
           ('ledbit', fmt.m16x, "INTEGER"),   # 0x0f
           ('sndbit', fmt.m8x, "INTEGER"),    # 0x07
           ('ffbit', fmt.m32x, "INTEGER"),    # 0x7f
           ('swbit', fmt.m16x, "INTEGER"),    # 0x0f
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class eisa_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "eisa")

    kind = ("linux-kernel", "device")

    cols = (('sig', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class parisc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "parisc")

    kind = ("linux-kernel", "device")

    cols = (('hw_type', fmt.m8x, "INTEGER"),
           ('hversion_rev', fmt.m8x, "INTEGER"),
           ('hversion', fmt.m16x, "INTEGER"),
           ('sversion', fmt.m32x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class sdio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "sdio")

    kind = ("linux-kernel", "device")

    cols = (('class', fmt.m8x, "INTEGER"),
           ('vendor', fmt.m16x, "INTEGER"),
           ('device', fmt.m16x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class ssb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ssb")

    kind = ("linux-kernel", "device")

    cols = (('vendor', fmt.m16x, "INTEGER"),
           ('coreid', fmt.m16x, "INTEGER"),
           ('revision', fmt.m8x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class virtio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "virtio")

    kind = ("linux-kernel", "device")

    cols = (('device', fmt.m32x, "INTEGER"),
           ('vendor', fmt.m32x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class i2c_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "i2c")

    kind = ("linux-kernel", "device")

    cols = (('name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class tc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "tc")

    kind = ("linux-kernel", "device")

    cols = (('vendor', fmt.qstr, "TEXT"),
	   ('name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class zorro_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "zorro")

    kind = ("linux-kernel", "device")

    cols = (('id1', fmt.m16x, "INTEGER"),
           ('id2', fmt.m16x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class agp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "agp")

    kind = ("linux-kernel", "device")

    cols = (('chipset', fmt.m16x, "INTEGER"),
	   ('chipset_name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


def register(tree):
    tree.register_table('pci', pci_table())
    tree.register_table('usb', usb_table())
    tree.register_table('ieee1394', ieee1394_table())
    tree.register_table('hid', hid_table())
    tree.register_table('ccw', ccw_table())
    tree.register_table('ap', ap_table())
    tree.register_table('acpi', acpi_table())
    tree.register_table('pnp', pnp_table())
    tree.register_table('serio', serio_table())
    tree.register_table('of', of_table())
    tree.register_table('vio', vio_table())
    tree.register_table('pcmcia', pcmcia_table())
    tree.register_table('input', input_table())
    tree.register_table('eisa', eisa_table())
    tree.register_table('parisc', parisc_table())
    tree.register_table('sdio', sdio_table())
    tree.register_table('ssb', ssb_table())
    tree.register_table('virtio', virtio_table())
    tree.register_table('i2c', i2c_table())
    tree.register_table('tc', tc_table())
    tree.register_table('zorro', zorro_table())
    tree.register_table('agp', agp_table())

