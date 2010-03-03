#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import fmt

class pci_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "pci", tree)

    cols = (('vendor', fmt.m16x, "INTEGER"),
	   ('device', fmt.m16x, "INTEGER"),
	   ('subvendor', fmt.m16x, "INTEGER"),
	   ('subdevice', fmt.m16x, "INTEGER"),
	   ('class', None, "INTEGER"),
           ('class_mask', fmt.special, "INTEGER"),
	   ('deps', fmt.deps, "$deps"),
	   ('filename', fmt.filename, "$filename"),
	   ('version', None, "$kver"))

    def add_row_fmt(self, row):
	m = fmt.mask_24m(fmt.m24x(row[4]), fmt.m24x(row[5]))
        lkddb.table.add_row_fmt(self, row[:4] + (m,) + row[6:])


class usb_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "usb", tree)

    cols = (('idVendor', fmt.m16x, "INTEGER"),
	   ('idProduct', fmt.m16x, "INTEGER"),
           ('bDeviceClass', fmt.m8x, "INTEGER"),
	   ('bDeviceSubClass', fmt.m8x, "INTEGER"),
	   ('bDeviceProtocol', fmt.m8x, "INTEGER"),
           ('bInterfaceClass', fmt.m8x, "INTEGER"),
	   ('bInterfaceSubClass', fmt.m8x, "INTEGER"),
	   ('bInterfaceProtocol', fmt.m8x, "INTEGER"),
           ('bcdDevice_lo', fmt.m16x, "INTEGER"),
	   ('bcdDevice_hi', fmt.m16x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class ieee1394_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "ieee1394", tree)

    cols = (('vendor_id', fmt.m24x, "INTEGER"),
	   ('model_id', fmt.m24x, "INTEGER"),
	   ('specifier_id', fmt.m24x, "INTEGER"),
	   ('version', fmt.m24x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class hid_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "hid", tree)

    cols = (('bus', fmt.m16x, "INTEGER"),
	   ('vendor', fmt.m32x, "INTEGER"),
	   ('product', fmt.m32x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class ccw_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "ccw", tree)

    cols = (('cu_type', fmt.m16x, "INTEGER"),
	   ('cu_model', fmt.m8x, "INTEGER"),
	   ('dev_type', fmt.m16x, "INTEGER"),
	   ('dev_model', fmt.m8x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


# s390 AP bus
class ap_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "ap", tree)

    cols = (('dev_type', fmt.m8x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class acpi_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "acpi", tree)

    cols = (('id', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class pnp_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "pnp", tree)

    cols = (('id', fmt.qstr, "TEXT"),
	   ('n0', fmt.qstr, "TEXT"),
	   ('n1', fmt.qstr, "TEXT"),
	   ('n2', fmt.qstr, "TEXT"),
	   ('n3', fmt.qstr, "TEXT"),
	   ('n4', fmt.qstr, "TEXT"),
	   ('n5', fmt.qstr, "TEXT"),
	   ('n6', fmt.qstr, "TEXT"),
	   ('n7', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class serio_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "serio", tree)

    cols = (('type', fmt.m8x, "INTEGER"),
           ('proto', fmt.m8x, "INTEGER"),
           ('id', fmt.m8x, "INTEGER"),
           ('extra', fmt.m8x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class of_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "of", tree)

    cols = (('name', fmt.qstr, "TEXT"),
	   ('type', fmt.qstr, "TEXT"),
	   ('compatible', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class vio_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "vio", tree)

    cols = (('type', fmt.qstr, "TEXT"),
           ('compat', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class pcmcia_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "pcmcia", tree)

    cols = (('manf_id', fmt.m16x, "INTEGER"),
           ('card_id', fmt.m16x, "INTEGER"),
           ('func_id', fmt.m8x, "INTEGER"),
           ('function', fmt.m8x, "INTEGER"),
           ('device_no', fmt.m8x, "INTEGER"),
           ('n0', fmt.qstr, "TEXT"),
           ('n1', fmt.qstr, "TEXT"),
           ('n2', fmt.qstr, "TEXT"),
           ('n3', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class input_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "input", tree)

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

    def __init__(self, tree):
        lkddb.table.__init__(self, "eisa", tree)

    cols = (('sig', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class parisc_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "parisc", tree)

    cols = (('hw_type', fmt.m8x, "INTEGER"),
           ('hversion_rev', fmt.m8x, "INTEGER"),
           ('hversion', fmt.m16x, "INTEGER"),
           ('sversion', fmt.m32x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class sdio_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "sdio", tree)

    cols = (('class', fmt.m8x, "INTEGER"),
           ('vendor', fmt.m16x, "INTEGER"),
           ('device', fmt.m16x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class ssb_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "ssb", tree)

    cols = (('vendor', fmt.m16x, "INTEGER"),
           ('coreid', fmt.m16x, "INTEGER"),
           ('revision', fmt.m8x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class virtio_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "virtio", tree)

    cols = (('device', fmt.m32x, "INTEGER"),
           ('vendor', fmt.m32x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class i2c_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "i2c", tree)

    cols = (('name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class tc_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "tc", tree)

    cols = (('vendor', fmt.qstr, "TEXT"),
	   ('name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class zorro_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "zorro", tree)

    cols = (('id1', fmt.m16x, "INTEGER"),
           ('id2', fmt.m16x, "INTEGER"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


class agp_table(lkddb.table):

    def __init__(self, tree):
        lkddb.table.__init__(self, "agp", tree)

    cols = (('chipset', fmt.m16x, "INTEGER"),
	   ('chipset_name', fmt.qstr, "TEXT"),
           ('deps', fmt.deps, "$deps"),
           ('filename', fmt.filename, "$filename"),
           ('version', None, "$kver"))


def register(tree):
    lkddb.register_table('pci', pci_table(tree))
    lkddb.register_table('usb', usb_table(tree))
    lkddb.register_table('ieee1394', ieee1394_table(tree))
    lkddb.register_table('hid', hid_table(tree))
    lkddb.register_table('ccw', ccw_table(tree))
    lkddb.register_table('ap', ap_table(tree))
    lkddb.register_table('acpi', acpi_table(tree))
    lkddb.register_table('pnp', pnp_table(tree))
    lkddb.register_table('serio', serio_table(tree))
    lkddb.register_table('of', of_table(tree))
    lkddb.register_table('vio', vio_table(tree))
    lkddb.register_table('pcmcia', pcmcia_table(tree))
    lkddb.register_table('input', input_table(tree))
    lkddb.register_table('eisa', eisa_table(tree))
    lkddb.register_table('parisc', parisc_table(tree))
    lkddb.register_table('sdio', sdio_table(tree))
    lkddb.register_table('ssb', ssb_table(tree))
    lkddb.register_table('virtio', virtio_table(tree))
    lkddb.register_table('i2c', i2c_table(tree))
    lkddb.register_table('tc', tc_table(tree))
    lkddb.register_table('zorro', zorro_table(tree))
    lkddb.register_table('agp', agp_table(tree))

