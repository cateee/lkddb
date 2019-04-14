#!/usr/bin/python
#: lkddb/tables/linux_devicetables.py : device tables for Linux kernel
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import lkddb
from lkddb import fmt
import lkddb.linux


@lkddb.register_to_group(lkddb.linux.tables)
class pci_table(lkddb.Table):

    def __init__(self):
        super().__init__("pci")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'vendor', fmt.m16x, "INTEGER"),
                     (2, 'device', fmt.m16x, "INTEGER"),
                     (3, 'subvendor', fmt.m16x, "INTEGER"),
                     (4, 'subdevice', fmt.m16x, "INTEGER"),
                     (-77, 'class', None, "INTEGER"),
                     (5, 'class_mask', fmt.special, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()

    def pre_row_fmt(self, row):
        m = fmt.mask_24m(fmt.m24x(row[4]), fmt.m24x(row[5]))
        return lkddb.Table.pre_row_fmt(self, row[:4] + (m,) + row[6:])


@lkddb.register_to_group(lkddb.linux.tables)
class usb_table(lkddb.Table):

    def __init__(self):
        super().__init__("usb")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'idVendor', fmt.m16x, "INTEGER"),
                     (2, 'idProduct', fmt.m16x, "INTEGER"),
                     (3, 'bDeviceClass', fmt.m8x, "INTEGER"),
                     (4, 'bDeviceSubClass', fmt.m8x, "INTEGER"),
                     (5, 'bDeviceProtocol', fmt.m8x, "INTEGER"),
                     (6, 'bInterfaceClass', fmt.m8x, "INTEGER"),
                     (7, 'bInterfaceSubClass', fmt.m8x, "INTEGER"),
                     (8, 'bInterfaceProtocol', fmt.m8x, "INTEGER"),
                     (9, 'bcdDevice_lo', fmt.m16x, "INTEGER"),
                     (10, 'bcdDevice_hi', fmt.m16x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class ieee1394_table(lkddb.Table):

    def __init__(self):
        super().__init__("ieee1394")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'vendor_id', fmt.m24x, "INTEGER"),
                     (2, 'model_id', fmt.m24x, "INTEGER"),
                     (3, 'specifier_id', fmt.m24x, "INTEGER"),
                     (4, 'version', fmt.m24x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class hid_table(lkddb.Table):

    def __init__(self):
        super().__init__("hid")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'bus', fmt.m16x, "INTEGER"),
                     (2, 'vendor', fmt.m32x, "INTEGER"),
                     (3, 'product', fmt.m32x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class ccw_table(lkddb.Table):

    def __init__(self):
        super().__init__("ccw")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'cu_type', fmt.m16x, "INTEGER"),
                     (2, 'cu_model', fmt.m8x, "INTEGER"),
                     (3, 'dev_type', fmt.m16x, "INTEGER"),
                     (4, 'dev_model', fmt.m8x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


# s390 AP bus
@lkddb.register_to_group(lkddb.linux.tables)
class ap_table(lkddb.Table):

    def __init__(self):
        super().__init__("ap")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'dev_type', fmt.m8x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class acpi_table(lkddb.Table):

    def __init__(self):
        super().__init__("acpi")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'id', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class pnp_table(lkddb.Table):

    def __init__(self):
        super().__init__("pnp")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'id', fmt.qstr, "TEXT"),
                     (2, 'n0', fmt.qstr, "TEXT"),
                     (3, 'n1', fmt.qstr, "TEXT"),
                     (4, 'n2', fmt.qstr, "TEXT"),
                     (5, 'n3', fmt.qstr, "TEXT"),
                     (6, 'n4', fmt.qstr, "TEXT"),
                     (7, 'n5', fmt.qstr, "TEXT"),
                     (8, 'n6', fmt.qstr, "TEXT"),
                     (9, 'n7', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class serio_table(lkddb.Table):

    def __init__(self):
        super().__init__("serio")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'type', fmt.m8x, "INTEGER"),
                     (2, 'proto', fmt.m8x, "INTEGER"),
                     (3, 'id', fmt.m8x, "INTEGER"),
                     (4, 'extra', fmt.m8x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class hda_table(lkddb.Table):

    def __init__(self):
        super().__init__("hda")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'vendor_id', fmt.m32x, "INTEGER"),
                     (2, 'rev_id', fmt.m32x, "INTEGER"),
                     (3, 'api_version', fmt.m8x, "INTEGER"),
                     (4, 'name', fmt.qstr, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class sdw_table(lkddb.Table):

    def __init__(self):
        super().__init__("sdw")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'mfg_id', fmt.m16x, "INTEGER"),
                     (2, 'part_id', fmt.m16x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class of_table(lkddb.Table):

    def __init__(self):
        super().__init__("of")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (2, 'type', fmt.qstr, "TEXT"),
                     (3, 'compatible', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class vio_table(lkddb.Table):

    def __init__(self):
        super().__init__("vio")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'type', fmt.qstr, "TEXT"),
                     (2, 'compat', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class pcmcia_table(lkddb.Table):

    def __init__(self):
        super().__init__("pcmcia")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'manf_id', fmt.m16x, "INTEGER"),
                     (2, 'card_id', fmt.m16x, "INTEGER"),
                     (3, 'func_id', fmt.m8x, "INTEGER"),
                     (4, 'function', fmt.m8x, "INTEGER"),
                     (5, 'device_no', fmt.m8x, "INTEGER"),
                     (6, 'n0', fmt.qstr, "TEXT"),
                     (7, 'n1', fmt.qstr, "TEXT"),
                     (8, 'n2', fmt.qstr, "TEXT"),
                     (9, 'n3', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class input_table(lkddb.Table):

    def __init__(self):
        super().__init__("input")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'bustype', fmt.m16x, "INTEGER"),
                     (2, 'vendor', fmt.m16x, "INTEGER"),
                     (3, 'product', fmt.m16x, "INTEGER"),
                     (4, 'version', fmt.m16x, "INTEGER"),
                     (5, 'evbit', fmt.m32x, "INTEGER"),  # 0x1f
                     (6, 'keybit', fmt.m32x, "INTEGER"),  # 0x2ff - 0x71
                     (7, 'relbit', fmt.m16x, "INTEGER"),  # 0x0f
                     (8, 'absbit', fmt.m64x, "INTEGER"),  # 0x3f
                     (9, 'mscbit', fmt.m8x, "INTEGER"),  # 0x07
                     (10, 'ledbit', fmt.m16x, "INTEGER"),  # 0x0f
                     (11, 'sndbit', fmt.m8x, "INTEGER"),  # 0x07
                     (12, 'ffbit', fmt.m64x, "INTEGER"),  # 0x7f
                     (13, 'swbit', fmt.m16x, "INTEGER"),  # 0x0f
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class eisa_table(lkddb.Table):

    def __init__(self):
        super().__init__("eisa")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'sig', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class parisc_table(lkddb.Table):

    def __init__(self):
        super().__init__("parisc")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'hw_type', fmt.m8x, "INTEGER"),
                     (2, 'hversion_rev', fmt.m8x, "INTEGER"),
                     (3, 'hversion', fmt.m16x, "INTEGER"),
                     (4, 'sversion', fmt.m32x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class sdio_table(lkddb.Table):

    def __init__(self):
        super().__init__("sdio")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'class', fmt.m8x, "INTEGER"),
                     (2, 'vendor', fmt.m16x, "INTEGER"),
                     (3, 'device', fmt.m16x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class ssb_table(lkddb.Table):

    def __init__(self):
        super().__init__("ssb")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'vendor', fmt.m16x, "INTEGER"),
                     (2, 'coreid', fmt.m16x, "INTEGER"),
                     (3, 'revision', fmt.m8x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class bcma_table(lkddb.Table):

    def __init__(self):
        super().__init__("bcma")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'manuf', fmt.m16x, "INTEGER"),
                     (2, 'id', fmt.m16x, "INTEGER"),
                     (3, 'rev', fmt.m8x, "INTEGER"),
                     (4, 'class', fmt.m8x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class virtio_table(lkddb.Table):

    def __init__(self):
        super().__init__("virtio")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'device', fmt.m32x, "INTEGER"),
                     (2, 'vendor', fmt.m32x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


# hv_vmbus_device_id
@lkddb.register_to_group(lkddb.linux.tables)
class rpmsg_table(lkddb.Table):

    def __init__(self):
        super().__init__("rpmsg")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class i2c_table(lkddb.Table):

    def __init__(self):
        super().__init__("i2c")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class pci_epf_table(lkddb.Table):

    def __init__(self):
        super().__init__("pci_epf")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class i3c_table(lkddb.Table):

    def __init__(self):
        super().__init__("i3c")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'match_flags', fmt.m8x, "INTEGER"),
                     (2, 'dcr', fmt.m8x, "INTEGER"),
                     (3, 'manuf_id', fmt.m16x, "INTEGER"),
                     (4, 'part_id', fmt.m16x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class spi_table(lkddb.Table):

    def __init__(self):
        super().__init__("spi")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class slim_table(lkddb.Table):

    def __init__(self):
        super().__init__("slim")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'manf_id', fmt.m16x, "INTEGER"),
                     (2, 'prod_code', fmt.m16x, "INTEGER"),
                     (3, 'dev_index', fmt.m16x, "INTEGER"),
                     (4, 'instance', fmt.m16x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class apr_table(lkddb.Table):

    def __init__(self):
        super().__init__("apr")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (2, 'domain_id', fmt.m32x, "INTEGER"),
                     (3, 'svc_id', fmt.m32x, "INTEGER"),
                     (4, 'svc_version', fmt.m32x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class spmi_table(lkddb.Table):

    def __init__(self):
        super().__init__("spmi")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


# platform_device_id

# mdio_device_id


@lkddb.register_to_group(lkddb.linux.tables)
class tc_table(lkddb.Table):

    def __init__(self):
        super().__init__("tc")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'vendor', fmt.qstr, "TEXT"),
                     (2, 'name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()


@lkddb.register_to_group(lkddb.linux.tables)
class zorro_table(lkddb.Table):

    def __init__(self):
        super().__init__("zorro")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'id1', fmt.m16x, "INTEGER"),
                     (2, 'id2', fmt.m16x, "INTEGER"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()

# isapnp_device_id

# amba_id

# mips_cdmm_device_id

# x86_cpu_id

# mei_cl_device_id


@lkddb.register_to_group(lkddb.linux.tables)
class agp_table(lkddb.Table):

    def __init__(self):
        super().__init__("agp")
        self.kind = ("linux-kernel", "device")
        self.cols = ((1, 'chipset', fmt.m16x, "INTEGER"),
                     (2, 'chipset_name', fmt.qstr, "TEXT"),
                     (-1, 'deps', fmt.deps, "$deps"),
                     (-2, 'filename', fmt.filename, "$filename"),
                     (-99, 'version', None, "$kver"))
        self.init_cols()
