#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb.fmt import *

class pci_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pci_table")

    names = ('vendor', 'device', 'subvendor', 'subdevice',
                        'class_mask', 'deps', 'filename')

    def add_row_fmt(self, row):
	m = fmt_mask_32m(fmt_m32x(row[4]), fmt_m32x(row[5]))
        lkddb.table.add_row_fmt(self, row[:4] + (m,) + row[6:])

    row_fmt = (fmt_m16x, fmt_m16x, fmt_m16x, fmt_m16x,
	       fmt_pass, fmt_deps, fmt_filename)
    line_templ = ("pci %s %s %s %s %s\t%s # %s\n")


class usb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "usb_table")

    names = ('idVendor', 'idProduct',
                'bDeviceClass', 'bDeviceSubClass', 'bDeviceProtocol',
                'bInterfaceClass', 'bInterfaceSubClass', 'bInterfaceProtocol',
                'bcdDevice_lo', 'bcdDevice_hi', 'deps', 'filename')

    row_fmt = (fmt_m16x, fmt_m16x,
		fmt_m8x, fmt_m8x, fmt_m8x,  fmt_m8x, fmt_m8x, fmt_m8x,
		fmt_m16x, fmt_m16x, fmt_deps, fmt_filename)
    line_templ = ("usb %s %s %s%s%s %s%s%s %s %s\t%s # %s\n")


class ieee1394_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ieee1394_table")

    row_fmt = (fmt_m32x, fmt_m32x, fmt_m32x, fmt_m32x,
		fmt_deps, fmt_filename)
    line_templ = ("ieee1394 %s %s %s %s\t%s # %s\n")
    names = ('vendor_id', 'model_id', 'specifier_id', 'version',
         'deps', 'filename')

#    fmt_line = ("ieee1394\t%(vendor_id)06x %(model_id)06x " +
#                "%(specifier_id)06x %(version)06x\t%(deps)s\t%(filename)s\n" )

class hid_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "hid_table")

    row_fmt = (fmt_m16x, fmt_m32x, fmt_m32x,
                fmt_deps, fmt_filename)
    line_templ = ("hid %s %s %s\t%s # %s\n")
    names = ("bus", "vendor", "product", 
         'deps', 'filename')
#    fmt_line = ('hid\t%(bus)04x %(vendor)08x %(product)08x' +
#                '\t%(deps)s\t%(filename)s\n' )


class ccw_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ccw_table")

    row_fmt = (fmt_m16x, fmt_m8x, fmt_m16x, fmt_m8x,
                fmt_deps, fmt_filename)
    line_templ = ("ccw %s %s %s %s\t%s # %s\n")
    names = ("cu_type","cu_model","dev_type","dev_model",
         'deps', 'filename')

    fmt_line = ('ccw\t%(cu_type)04x %(cu_model)02x %(dev_type)04x %(dev_model)02x' +
                '\t%(deps)s\t%(filename)s\n' )


# s390 AP bus
class ap_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "ap_table")

    row_fmt = (fmt_m8x,
                fmt_deps, fmt_filename)
    line_templ = ("ap %s\t%s # %s\n")
    names = ("dev_type", 
         'deps', 'filename')
    fmt_line = ('ap\t%(dev_type)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class acpi_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "acpi_table")

    row_fmt = (fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("acpi %s\t%s # %s\n")
    names = ("id",
         'deps', 'filename')
    fmt_line = ('acpi\t%(id)s' +
                '\t%(deps)s\t%(filename)s\n' )

class pnp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pnp_table")

    row_fmt = (fmt_qstr, fmt_qstr, fmt_qstr, fmt_qstr, fmt_qstr,
		fmt_qstr, fmt_qstr, fmt_qstr, fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("pnp %s %s %s %s %s %s %s %s %s\t%s # %s\n")
    names = ("id", "n0", "n1","n2","n3","n4","n5","n6","n7",
         'deps', 'filename')
    fmt_line = ('pnp\t%(id)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class serio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "serio_table")

    row_fmt = (fmt_m8x, fmt_m8x, fmt_m8x, fmt_m8x,
                fmt_deps, fmt_filename)
    line_templ = ("serio %s %s %s %s\t%s # %s\n")
    names = ("type", "extra", "id", "proto", 
         'deps', 'filename')
    fmt_line = ('serio\t%(type)02x %(extra)02x %(id)02x %(proto)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class of_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "of_table")

    row_fmt = (fmt_qstr, fmt_qstr, fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("of %s %s %s\t%s # %s\n")
    names = ("name", "type", "compatible", 
         'deps', 'filename')
    fmt_line = ('of\t%(type)02x %(extra)02x %(id)02x %(proto)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class vio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "vio_table")

    row_fmt = (fmt_qstr, fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("vio %s %s\t%s # %s\n")
    names = ("type", "compat", 
         'deps', 'filename')
    fmt_line = ('vio\t%(type)s %(compat)s' +
                '\t%(deps)s\t%(filename)s\n' )


class pcmcia_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "pcmcia_table")

    row_fmt = (fmt_m16x, fmt_m16x, fmt_m8x, fmt_m8x, fmt_m8x,
		fmt_qstr, fmt_qstr, fmt_qstr, fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("pcmcia %s %s %s %s %s %s %s %s %s\t%s # %s\n")
    names = ("manf_id", "card_id", "func_id", "function", "device_no",
	  "n1", "n2", "n3", "n4",
         'deps', 'filename')
    fmt_line = ('pcmcia\t%(manf_id)04x %(card_id)04x %(func_id)02x %(function)02x %(device_no)02x ' +
                '"%(n1)s" "%(n2)s" "%(n3)s" "%(n4)s"' +
                '\t%(deps)s\t%(filename)s\n' )


class input_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "input_table")

    row_fmt = (fmt_m16x, fmt_m16x, fmt_m16x, fmt_m16x,
		fmt_m8x, fmt_m8x, fmt_m8x, fmt_m8x, fmt_m8x, fmt_m8x, fmt_m8x,
		fmt_m8x, fmt_m8x,
                fmt_deps, fmt_filename)
    line_templ = ("input %s %s %s %s %s %s %s %s %s %s %s %s %s\t%s # %s\n")
    names = ("bustype", "vendor", "product", "version",
    "evbit", "keybit", "relbit", "absbit", "mscbit", "ledbit", "sndbit", "ffbit", "swbit",
         'deps', 'filename')
    fmt_line = ('input\t%(bustype)04x %(vendor)04x %(product)04x %(version)04x ' +
                '%(evbit)02x %(keybit)02x %(relbit)02x %(absbit)02x %(mscbit)02x ' +
                '%(sndbit)02x %(ffbit)02x %(swbit)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class eisa_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "eisa_table")

    row_fmt = (fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("eisa %s\t%s # %s\n")
    names = ("sig",
         'deps', 'filename')
    fmt_line = ('eisa\t%(sig)s' +
                '\t%(deps)s\t%(filename)s\n' )


class parisc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "parisc_table")

    row_fmt = (fmt_m8x, fmt_m8x, fmt_m16x, fmt_m32x,
                fmt_deps, fmt_filename)
    line_templ = ("parisc %s %s %s %s\t%s # %s\n")
    names = ("hw_type", "hversion_rev", "hversion", "sversion",
         'deps', 'filename')
    fmt_line = ('parisc\t%(hw_type)02x %(hversion_rev)02x %(hversion)04x %(sversion)08x' +
                '\t%(deps)s\t%(filename)s\n' )


class sdio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "sdio_table")

    row_fmt = (fmt_m8x, fmt_m16x, fmt_m16x,
                fmt_deps, fmt_filename)
    line_templ = ("sdio %s %s %s\t%s # %s\n")
    names = ("class", "vendor", "device",
         'deps', 'filename')
    fmt_line = ('sdio\t%(class)02x %(vendor)04x %(device)04x' +
                '\t%(deps)s\t%(filename)s\n' )


class sbb_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "sbb_table")

    row_fmt = (fmt_m16x, fmt_m16x, fmt_m16x,
                fmt_deps, fmt_filename)
    line_templ = ("sbb %s %s %s\t%s # %s\n")
    names = ("vendor", "coreid", "revision",
         'deps', 'filename')
    fmt_line = ('sbb\t%(vendor)04x %(coreid)04x %(revision)02x' +
                '\t%(deps)s\t%(filename)s\n' )


class virtio_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "virtio_table")

    row_fmt = (fmt_m32x, fmt_m32x,
                fmt_deps, fmt_filename)
    line_templ = ("virtio %s %s\t%s # %s\n")
    names = ("device", "vendor",
         'deps', 'filename')
    fmt_line = ('virtio\t%(device)08x %(vendor)08x' +
                '\t%(deps)s\t%(filename)s\n' )

class i2c_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "i2c_table")

    row_fmt = (fmt_qstr, 
                fmt_deps, fmt_filename)
    line_templ = ("i2c %s\t%s # %s\n")
    names = ("name",
         'deps', 'filename')
    fmt_line = ('i2c\t%(name)s' +
                '\t%(deps)s\t%(filename)s\n' )


class tc_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "tc_table")

    row_fmt = (fmt_qstr, fmt_qstr,
                fmt_deps, fmt_filename)
    line_templ = ("tc %s %s\t%s # %s\n")
    names = ("vendor", "name",
         'deps', 'filename')
    fmt_line = ('tc\t%(vendor)s %(name)s' +
                '\t%(deps)s\t%(filename)s\n' )


class zorro_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "zorro_table")

    row_fmt = (fmt_m16x, fmt_m16x,
                fmt_deps, fmt_filename)
    line_templ = ("zorro %s %s\t%s # %s\n")
    names = ("id1", "id2",
         'deps', 'filename')
    fmt_line = ('zorro\t%(id1)04x %(id2)04x' +
                '\t%(deps)s\t%(filename)s\n' )


class agp_table(lkddb.table):

    def __init__(self):
        lkddb.table.__init__(self, "agp_table")

    row_fmt = (fmt_m16x,
                fmt_deps, fmt_filename)
    line_templ = ("agp %s %s\t%s # %s\n")
    names = ("chipset", "chipset_name",
         'deps', 'filename')
    fmt_line = ('agp\t%(chipset)04x %(chipset_name)s' +
                '\t%(deps)s\t%(filename)s\n' )


def register():
#    lkddb.register_table('', _table)
    lkddb.register_table('pci', pci_table())
    lkddb.register_table('usb', usb_table())
    lkddb.register_table('ieee1394', ieee1394_table())
    lkddb.register_table('hid', hid_table())
    lkddb.register_table('ccw', ccw_table())
    lkddb.register_table('ap', ap_table())
    lkddb.register_table('acpi', acpi_table())
    lkddb.register_table('pnp', pnp_table())
#    lkddb.register_table('pnp2', pnp2_table())
    lkddb.register_table('serio', serio_table())
    lkddb.register_table('of', of_table())
    lkddb.register_table('vio', vio_table())
    lkddb.register_table('pcmcia', pcmcia_table())
    lkddb.register_table('input', input_table())
    lkddb.register_table('eisa', eisa_table())
    lkddb.register_table('parisc', parisc_table())
    lkddb.register_table('sdio', sdio_table())
    lkddb.register_table('sbb', sbb_table())
    lkddb.register_table('virtio', virtio_table())
    lkddb.register_table('i2c', i2c_table())
    lkddb.register_table('tc', tc_table())
    lkddb.register_table('zorro', zorro_table())
    lkddb.register_table('agp', agp_table())


