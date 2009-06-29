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

    cols = (('vendor', fmt.m16x, "INTEGER"),
	   ('device', fmt.m16x, "INTEGER"),
	   ('subvendor', fmt.m16x, "INTEGER"),
	   ('subdevice', fmt.m16x, "INTEGER"),
	   ('class', None, "INTEGER"),
           ('class_mask', fmt.special, "INTEGER"),
	   ('deps', fmt.deps, "..."),
	   ('filename', fmt.filename, "...."))

    def add_row_fmt(self, row):
	m = fmt.mask_24m(fmt.m24x(row[4]), fmt.m24x(row[5]))
        lkddb.table.add_row_fmt(self, row[:4] + (m,) + row[6:])


class usb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "usb")

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
	   ('deps',  fmt.deps, "..."),
	   ('filename', fmt.filename, "...."))


class ieee1394_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ieee1394")

    cols = (('vendor_id', fmt.m24x, "INTEGER"),
	   ('model_id', fmt.m24x, "INTEGER"),
	   ('specifier_id', fmt.m24x, "INTEGER"),
	   ('version', fmt.m24x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class hid_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "hid")

    cols = (('bus', fmt.m16x, "INTEGER"),
	   ('vendor', fmt.m32x, "INTEGER"),
	   ('product', fmt.m32x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class ccw_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ccw")

    cols = (('cu_type', fmt.m16x, "INTEGER"),
	   ('cu_model', fmt.m8x, "INTEGER"),
	   ('dev_type', fmt.m16x, "INTEGER"),
	   ('dev_model', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


# s390 AP bus
class ap_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ap")

    cols = (('dev_type', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class acpi_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "acpi")

    cols = (('id', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class pnp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pnp")

    cols = (('id', fmt.qstr, "TEXT"),
	   ('n0', fmt.qstr, "TEXT"),
	   ('n1', fmt.qstr, "TEXT"),
	   ('n2', fmt.qstr, "TEXT"),
	   ('n3', fmt.qstr, "TEXT"),
	   ('n4', fmt.qstr, "TEXT"),
	   ('n5', fmt.qstr, "TEXT"),
	   ('n6', fmt.qstr, "TEXT"),
	   ('n7', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class serio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "serio")

    cols = (('type', fmt.m8x, "INTEGER"),
           ('proto', fmt.m8x, "INTEGER"),
           ('id', fmt.m8x, "INTEGER"),
           ('extra', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class of_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "of")

    cols = (('name', fmt.qstr, "TEXT"),
	   ('type', fmt.qstr, "TEXT"),
	   ('compatible', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class vio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "vio")

    cols = (('type', fmt.qstr, "TEXT"),
           ('compat', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class pcmcia_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pcmcia")

    cols = (('manf_id', fmt.m16x, "INTEGER"),
           ('card_id', fmt.m16x, "INTEGER"),
           ('func_id', fmt.m8x, "INTEGER"),
           ('function', fmt.m8x, "INTEGER"),
           ('device_no', fmt.m8x, "INTEGER"),
           ('n0', fmt.qstr, "TEXT"),
           ('n1', fmt.qstr, "TEXT"),
           ('n2', fmt.qstr, "TEXT"),
           ('n3', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class input_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "input")

    cols = (('bustype', fmt.m16x, "INTEGER"),
           ('vendor', fmt.m16x, "INTEGER"),
           ('product', fmt.m16x, "INTEGER"),
           ('version', fmt.m16x, "INTEGER"),
           ('evbit', fmt.m8x, "INTEGER"),
           ('keybit', fmt.m16x, "INTEGER"),
           ('relbit', fmt.m8x, "INTEGER"),
           ('absbit', fmt.m8x, "INTEGER"),
           ('mscbit', fmt.m8x, "INTEGER"),
           ('ledbit', fmt.m8x, "INTEGER"),
           ('sndbit', fmt.m8x, "INTEGER"),
           ('ffbit', fmt.m8x, "INTEGER"),
           ('swbit', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class eisa_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "eisa")

    cols = (('sig', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class parisc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "parisc")

    cols = (('hw_type', fmt.m8x, "INTEGER"),
           ('hversion_rev', fmt.m8x, "INTEGER"),
           ('hversion', fmt.m16x, "INTEGER"),
           ('sversion', fmt.m32x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class sdio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "sdio")

    cols = (('class', fmt.m8x, "INTEGER"),
           ('vendor', fmt.m16x, "INTEGER"),
           ('device', fmt.m16x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class ssb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ssb")

    cols = (('vendor', fmt.m16x, "INTEGER"),
           ('coreid', fmt.m16x, "INTEGER"),
           ('revision', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class virtio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "virtio")

    cols = (('device', fmt.m32x, "INTEGER"),
           ('vendor', fmt.m32x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class i2c_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "i2c")

    cols = (('name', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class tc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "tc")

    cols = (('vendor', fmt.qstr, "TEXT"),
	   ('name', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class zorro_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "zorro")

    cols = (('id1', fmt.m16x, "INTEGER"),
           ('id2', fmt.m16x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


class agp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "agp")

    cols = (('chipset', fmt.m16x, "INTEGER"),
	   ('chipset_name', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


def register():
    lkddb.register_table('pci', pci_table())
    lkddb.register_table('usb', usb_table())
    lkddb.register_table('ieee1394', ieee1394_table())
    lkddb.register_table('hid', hid_table())
    lkddb.register_table('ccw', ccw_table())
    lkddb.register_table('ap', ap_table())
    lkddb.register_table('acpi', acpi_table())
    lkddb.register_table('pnp', pnp_table())
    lkddb.register_table('serio', serio_table())
    lkddb.register_table('of', of_table())
    lkddb.register_table('vio', vio_table())
    lkddb.register_table('pcmcia', pcmcia_table())
    lkddb.register_table('input', input_table())
    lkddb.register_table('eisa', eisa_table())
    lkddb.register_table('parisc', parisc_table())
    lkddb.register_table('sdio', sdio_table())
    lkddb.register_table('ssb', ssb_table())
    lkddb.register_table('virtio', virtio_table())
    lkddb.register_table('i2c', i2c_table())
    lkddb.register_table('tc', tc_table())
    lkddb.register_table('zorro', zorro_table())
    lkddb.register_table('agp', agp_table())

