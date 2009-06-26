#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import fmt

class pci_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pci_table")

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

    row_fmt = (fmt.m16x, fmt.m16x, fmt.m16x, fmt.m16x,
	       fmt.special, fmt.deps, fmt.filename)
    line_templ = ("pci\t%s %s %s %s %s\t%s\t%s\n")


class usb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "usb_table")

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

    row_fmt = (fmt.m16x, fmt.m16x,
		fmt.m8x, fmt.m8x, fmt.m8x,  fmt.m8x, fmt.m8x, fmt.m8x,
		fmt.m16x, fmt.m16x, fmt.deps, fmt.filename)
    line_templ = ("usb %s %s %s%s%s %s%s%s %s %s\t%s\t%s\n")


class ieee1394_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ieee1394_table")

    cols = (('vendor_id', fmt.m24x, "INTEGER"),
	   ('model_id', fmt.m24x, "INTEGER"),
	   ('specifier_id', fmt.m24x, "INTEGER"),
	   ('version', fmt.m24x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m24x, fmt.m24x, fmt.m24x, fmt.m24x,
		fmt.deps, fmt.filename)
    line_templ = ("ieee1394 %s %s %s %s\t%s\t%s\n")
#    fmt_line = ("ieee1394\t%(vendor_id)06x %(model_id)06x " +
#                "%(specifier_id)06x %(version)06x\t%(deps)s\t%(filename)s\n" )

class hid_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "hid_table")

    cols = (('bus', fmt.m16x, "INTEGER"),
	   ('vendor', fmt.m32x, "INTEGER"),
	   ('product', fmt.m32x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m16x, fmt.m32x, fmt.m32x,
                fmt.deps, fmt.filename)
    line_templ = ("hid %s %s %s\t%s\t%s\n")
#    fmt_line = ('hid\t%(bus)04x %(vendor)08x %(product)08x' +
#                '\t%(deps)s\t%(filename)s\n' )


class ccw_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ccw_table")

    cols = (('cu_type', fmt.m16x, "INTEGER"),
	   ('cu_model', fmt.m8x, "INTEGER"),
	   ('dev_type', fmt.m16x, "INTEGER"),
	   ('dev_model', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m16x, fmt.m8x, fmt.m16x, fmt.m8x,
                fmt.deps, fmt.filename)
    line_templ = ("ccw %s %s %s %s\t%s\t%s\n")
    fmt_line = ('ccw\t%(cu_type)04x %(cu_model)02x %(dev_type)04x %(dev_model)02x' +
                '\t%(deps)s\t%(filename)s\n' )


# s390 AP bus
class ap_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ap_table")

    cols = (('dev_type', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m8x,
                fmt.deps, fmt.filename)
    line_templ = ("ap %s\t%s\t%s\n")
    fmt_line = ('ap\t%(dev_type)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class acpi_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "acpi_table")

    cols = (('id', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.qstr,
                fmt.deps, fmt.filename)
    line_templ = ("acpi %s\t%s\t%s\n")
    names = ("id",
         'deps', 'filename')
    fmt_line = ('acpi\t%(id)s' +
                '\t%(deps)s\t%(filename)s\n' )

class pnp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pnp_table")

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

    row_fmt = (fmt.qstr, fmt.qstr, fmt.qstr, fmt.qstr, fmt.qstr,
		fmt.qstr, fmt.qstr, fmt.qstr, fmt.qstr,
                fmt.deps, fmt.filename)
    line_templ = ("pnp %s %s %s %s %s %s %s %s %s\t%s\t%s\n")
    fmt_line = ('pnp\t%(id)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class serio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "serio_table")

    cols = (('type', fmt.m8x, "INTEGER"),
           ('proto', fmt.m8x, "INTEGER"),
           ('id', fmt.m8x, "INTEGER"),
           ('extra', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m8x, fmt.m8x, fmt.m8x, fmt.m8x,
                fmt.deps, fmt.filename)
    line_templ = ("serio %s %s %s %s\t%s\t%s\n")
    names = ("type", "proto", "id", "extra", 
         'deps', 'filename')
    fmt_line = ('serio\t%(type)02x %(extra)02x %(id)02x %(proto)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class of_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "of_table")

    cols = (('name', fmt.qstr, "TEXT"),
	   ('type', fmt.qstr, "TEXT"),
	   ('compatible', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.qstr, fmt.qstr, fmt.qstr,
                fmt.deps, fmt.filename)
    line_templ = ("of %s %s %s\t%s\t%s\n")
    names = ("name", "type", "compatible", 
         'deps', 'filename')
    fmt_line = ('of\t%(type)02x %(extra)02x %(id)02x %(proto)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class vio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "vio_table")

   cols = (('type', fmt.qstr, "TEXT"),
           ('compat', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.qstr, fmt.qstr,
               fmt.deps, fmt.filename)
    line_templ = ("vio %s %s\t%s\t%s\n")
    names = ("type", "compat", 
         'deps', 'filename')
    fmt_line = ('vio\t%(type)s %(compat)s' +
                '\t%(deps)s\t%(filename)s\n' )


class pcmcia_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pcmcia_table")

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

    row_fmt = (fmt.m16x, fmt.m16x, fmt.m8x, fmt.m8x, fmt.m8x,
	       fmt.qstr, fmt.qstr, fmt.qstr, fmt.qstr,
               fmt.deps, fmt.filename)
    line_templ = ("pcmcia %s %s %s %s %s %s %s %s %s\t%s\t%s\n")
    names = ("manf_id", "card_id", "func_id", "function", "device_no",
	  "n1", "n2", "n3", "n4",
         'deps', 'filename')
    fmt_line = ('pcmcia\t%(manf_id)04x %(card_id)04x %(func_id)02x %(function)02x %(device_no)02x ' +
                '"%(n1)s" "%(n2)s" "%(n3)s" "%(n4)s"' +
                '\t%(deps)s\t%(filename)s\n' )


class input_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "input_table")

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

    row_fmt = (fmt.m16x, fmt.m16x, fmt.m16x, fmt.m16x,
	       fmt.m8x, fmt.m16x, fmt.m8x, fmt.m8x, fmt.m8x, fmt.m8x, fmt.m8x,
	       fmt.m8x, fmt.m8x,
               fmt.deps, fmt.filename)
    line_templ = ("input %s %s %s %s %s %s %s %s %s %s %s %s %s\t%s\t%s\n")
    fmt_line = ('input\t%(bustype)04x %(vendor)04x %(product)04x %(version)04x ' +
                '%(evbit)02x %(keybit)02x %(relbit)02x %(absbit)02x %(mscbit)02x ' +
                '%(sndbit)02x %(ffbit)02x %(swbit)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class eisa_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "eisa_table")

   cols = (('sig', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.qstr,
                fmt.deps, fmt.filename)
    line_templ = ("eisa %s\t%s\t%s\n")
    fmt_line = ('eisa\t%(sig)s' +
                '\t%(deps)s\t%(filename)s\n' )


class parisc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "parisc_table")

    cols = (('hw_type', fmt.m8x, "INTEGER"),
           ('hversion_rev', fmt.m8x, "INTEGER"),
           ('hversion', fmt.m16x, "INTEGER"),
           ('sversion', fmt.m32x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m8x, fmt.m8x, fmt.m16x, fmt.m32x,
                fmt.deps, fmt.filename)
    line_templ = ("parisc %s %s %s %s\t%s\t%s\n")


class sdio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "sdio_table")

    cols = (('class', fmt.m8x, "INTEGER"),
           ('vendor', fmt.m16x, "INTEGER"),
           ('device', fmt.m16x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m8x, fmt.m16x, fmt.m16x,
               fmt.deps, fmt.filename)
    line_templ = ("sdio %s %s %s\t%s\t%s\n")


class ssb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ssb_table")

    row_fmt = (fmt.m16x, fmt.m16x, fmt.m8x,
               fmt.deps, fmt.filename)

    cols = (('vendor', fmt.m16x, "INTEGER"),
           ('coreid', fmt.m16x, "INTEGER"),
           ('revision', fmt.m8x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    line_templ = ("ssb %s %s %s\t%s\t%s\n")
    fmt_line = ('ssb\t%(vendor)04x %(coreid)04x %(revision)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class virtio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "virtio_table")

    cols = (('device', fmt.m32x, "INTEGER"),
           ('vendor', fmt.m32x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m32x, fmt.m32x,
               fmt.deps, fmt.filename)
    line_templ = ("virtio %s %s\t%s\t%s\n")
    fmt_line = ('virtio\t%(device)08x %(vendor)08x' +
                '\t%(deps)s\t%(filename)s\n' )

class i2c_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "i2c_table")

    cols = (('name', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.qstr, 
               fmt.deps, fmt.filename)
    line_templ = ("i2c %s\t%s\t%s\n")
    fmt_line = ('i2c\t%(name)s' +
                '\t%(deps)s\t%(filename)s\n' )


class tc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "tc_table")

    cols = (('vendor', fmt.qstr, "TEXT"),
	   ('name', fmt.qstr, "TEXT"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.qstr, fmt.qstr,
               fmt.deps, fmt.filename)
    line_templ = ("tc %s %s\t%s\t%s\n")
    names = ("vendor", "name",
         'deps', 'filename')
    fmt_line = ('tc\t%(vendor)s %(name)s' +
                '\t%(deps)s\t%(filename)s\n' )


class zorro_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "zorro_table")

    cols = (('id1', fmt.m16x, "INTEGER"),
           ('id2', fmt.m16x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))


    row_fmt = (fmt.m16x, fmt.m16x,
               fmt.deps, fmt.filename)
    line_templ = ("zorro %s %s\t%s\t%s\n")
    names = ("id1", "id2",
         'deps', 'filename')
    fmt_line = ('zorro\t%(id1)04x %(id2)04x' +
                '\t%(deps)s\t%(filename)s\n' )


class agp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "agp_table")

    cols = (('chipset', fmt.m16x, "INTEGER"),
           ('deps',  fmt.deps, "..."),
           ('filename', fmt.filename, "...."))

    row_fmt = (fmt.m16x,
               fmt.deps, fmt.filename)
    line_templ = ("agp %s %s\t%s\t%s\n")
    names = ("chipset", "chipset_name",
         'deps', 'filename')
    fmt_line = ('agp\t%(chipset)04x %(chipset_name)s' +
                '\t%(deps)s\t%(filename)s\n' )


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

