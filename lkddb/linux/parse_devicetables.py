#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb.linux.scanners import *
from .browse_sources import struct_parent_scanner, parse_struct


# device_driver include/linux/device.h
device_driver_fields = (
    "name", "bus", "kobj", "klist_devices", "knode_bus", "owner", "mod_name",
    "mkobj", "probe", "remove", "shutdown", "suspend", "resume")

# Unwind some arrays (i.e. in pcmcia_device_id):
unwind_array = ("n0", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9")

class intern_scanner(object):
    def __init__(self, name):
        self.name = name


# PCI
#    include/linux/mod_devicetable.h pci_device_id
#    drivers/pci/pci-driver.c pci_match_id

class pci(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
      	  name = 'pci',
          tree = tree,
          table_name = 'pci',
	  parent_scanner = parent_scanner,
          struct_name = "pci_device_id",
          struct_fields = ("vendor", "device", "subvendor", "subdevice",
                   "class", "class_mask", "driver_data"),
          )

    def store(self, dict):
        v0 = extract_value("vendor", dict)
        v1 = extract_value("device", dict)
	v4b = extract_value("class_mask",dict)
        if v0 == 0 and v1 == 0 and v4b == 0:
            return None
        v2 = extract_value("subvendor", dict)
        v3 = extract_value("subdevice", dict)
        v4a = extract_value("class", dict)
        return (v0, v1, v2, v3, v4a, v4b)

#
# USB bus
#

class usb(list_of_structs_scanner):
    USB_DEVICE_ID_MATCH_VENDOR       = 0x0001
    USB_DEVICE_ID_MATCH_PRODUCT      = 0x0002
    USB_DEVICE_ID_MATCH_DEV_LO       = 0x0004
    USB_DEVICE_ID_MATCH_DEV_HI       = 0x0008
    USB_DEVICE_ID_MATCH_DEV_CLASS    = 0x0010
    USB_DEVICE_ID_MATCH_DEV_SUBCLASS = 0x0020
    USB_DEVICE_ID_MATCH_DEV_PROTOCOL = 0x0040
    USB_DEVICE_ID_MATCH_INT_CLASS    = 0x0080
    USB_DEVICE_ID_MATCH_INT_SUBCLASS = 0x0100
    USB_DEVICE_ID_MATCH_INT_PROTOCOL = 0x0200

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'usb',
          tree = tree,
	  table_name = 'usb',
          parent_scanner = parent_scanner,
          struct_name = "usb_device_id",
          struct_fields = (
	    "match_flags", "idVendor", "idProduct", "bcdDevice_lo", "bcdDevice_hi",
	    "bDeviceClass", "bDeviceSubClass", "bDeviceProtocol",
	    "bInterfaceClass", "bInterfaceSubClass", "bInterfaceProtocol",
	    "driver_info" )
          )

    def store(self, dict):
	match = extract_value("match_flags", dict)
        if not match:
            return None
	v0=-1; v1=-1; v2=-1; v3=-1; v4=-1; v5=-1; v6=-1; v7=-1
	v8 = 0; v9 = 0xffff
	if match & self.USB_DEVICE_ID_MATCH_VENDOR:
            v0 = extract_value("idVendor", dict)
        if match & self.USB_DEVICE_ID_MATCH_PRODUCT:
            v1 = extract_value("idProduct", dict)
        if match & self.USB_DEVICE_ID_MATCH_DEV_LO:
            v8 = extract_value("bcdDevice_lo", dict)
        if match & self.USB_DEVICE_ID_MATCH_DEV_HI:
            v9 = extract_value("bcdDevice_hi", dict)
        if match & self.USB_DEVICE_ID_MATCH_DEV_CLASS:
            v2 = extract_value("bDeviceClass", dict)
        if match & self.USB_DEVICE_ID_MATCH_DEV_SUBCLASS:
            v3 = extract_value("bDeviceSubClass", dict)
        if match & self.USB_DEVICE_ID_MATCH_DEV_PROTOCOL:
            v4 = extract_value("bDeviceProtocol", dict)
        if match & self.USB_DEVICE_ID_MATCH_INT_CLASS:
            v5 = extract_value("bInterfaceClass", dict)
        if match & self.USB_DEVICE_ID_MATCH_INT_SUBCLASS:
            v6 = extract_value("bInterfaceSubClass", dict)
        if match & self.USB_DEVICE_ID_MATCH_INT_PROTOCOL:
            v7 = extract_value("bInterfaceProtocol", dict)
        return (v0, v1, v2, v3, v4, v5, v6, v7, v8, v9)

#
# IEEE1394 bus
#

class ieee1394(list_of_structs_scanner):
    IEEE1394_MATCH_VENDOR_ID    = 0x0001
    IEEE1394_MATCH_MODEL_ID     = 0x0002
    IEEE1394_MATCH_SPECIFIER_ID = 0x0004
    IEEE1394_MATCH_VERSION      = 0x0008

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'ieee1394',
          tree = tree,
	  table_name = 'ieee1394',
          parent_scanner = parent_scanner,
          struct_name = "ieee1394_device_id",
          struct_fields = ("match_flags", "vendor_id", "model_id", "specifier_id",
		"version", "driver_data")
          )

    def store(self, dict):
        match = extract_value("match_flags", dict)
        if not match:
            return None
	v0=-1; v1=-1; v2=-1; v3=-1
        if match & self.IEEE1394_MATCH_VENDOR_ID:
            v0 = extract_value("vendor_id", dict)
        if match & self.IEEE1394_MATCH_MODEL_ID:
            v1  = extract_value("model_id", dict)
        if match & self.IEEE1394_MATCH_SPECIFIER_ID:
            v2  = extract_value("specifier_id", dict)
        if match & self.IEEE1394_MATCH_VERSION:
            v3  = extract_value("version", dict)
        return (v0, v1, v2, v3)


class hid(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'hid',
          tree = tree,
          table_name = 'hid',
          parent_scanner = parent_scanner,
          struct_name = "hid_device_id",
          struct_fields = ("bus", "vendor", "product", "driver_data")
          )

    def store(self, dict):
        v0 = extract_value("bus", dict)
        v1 = extract_value("vendor", dict)
        v2 =  extract_value("product",dict)
	if v0 == 0 and v1 == 0 and v2  == 0:
	    return None
	return (v0, v1, v2)



class ccw(list_of_structs_scanner):
    CCW_DEVICE_ID_MATCH_CU_TYPE      = 0x01
    CCW_DEVICE_ID_MATCH_CU_MODEL     = 0x02
    CCW_DEVICE_ID_MATCH_DEVICE_TYPE  = 0x04
    CCW_DEVICE_ID_MATCH_DEVICE_MODEL = 0x08

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'ccw',
          tree = tree,
          table_name = 'ccw',
          parent_scanner = parent_scanner,
          struct_name = "ccw_device_id",
          struct_fields = ("match_flags", "cu_type", "dev_type",
				"cu_model", "dev_model", "driver_info")
          )

    def store(self, dict):
        match = extract_value("match_flags", dict)
        if not match:
            return None
	v0=-1; v1=-1; v2=-1; v3=-1
        if match & self.CCW_DEVICE_ID_MATCH_CU_TYPE:
            v0 = extract_value("cu_type", dict)
        if match & self.CCW_DEVICE_ID_MATCH_CU_MODEL:
            v1  = extract_value("cu_model", dict)
        if match & self.CCW_DEVICE_ID_MATCH_DEVICE_TYPE:
            v2  = extract_value("dev_type", dict)
        if match & self.CCW_DEVICE_ID_MATCH_DEVICE_MODEL:
            v3  = extract_value("dev_model", dict)
        return (v0, v1, v2, v3)


# s390 AP bus devices ap_device_id include/linux/mod_devicetable.h

class ap(list_of_structs_scanner):
    AP_DEVICE_ID_MATCH_DEVICE_TYPE = 0x01

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'ap',
          tree = tree,
          table_name = 'ap',
          parent_scanner = parent_scanner,
          struct_name = "ap_device_id",
          struct_fields = ("match_flags", "dev_type", "pad1", "pad2", "driver_info")
          )

    def store(self, dict):
        match = extract_value("match_flags", dict)
        if not match:
            return None
        if match & self.AP_DEVICE_ID_MATCH_DEVICE_TYPE:
            v0 = extract_value("dev_type", dict)
        else:
            v0 = -1
        return (v0,)


# ACPI , acpi_device_id include/linux/mod_devicetable.h drivers/acpi/scan.c

class acpi(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'acpi',
          tree = tree,
          table_name = 'acpi',
          parent_scanner = parent_scanner,
          struct_name = "acpi_device_id",
          struct_fields = ("id", "driver_data")
          )

    def store(self, dict):
        v0 = extract_string("id", dict)
	if not v0:
	    return None
        return (v0,)


# PNP #1, pnp_device_id include/linux/mod_devicetable.h drivers/pnp/driver.c

class pnp(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'pnp',
          tree = tree,
          table_name = 'pnp',
          parent_scanner = parent_scanner,
          struct_name = "pnp_device_id",
          struct_fields = ("id", "driver_data")
          )

    def store(self, dict):
        v0 = extract_string("id", dict)
	if not v0:
	    return None
        return (v0,  "","","","",  "","","","")


# PNP #2, pnp_card_device_id include/linux/mod_devicetable.h drivers/pnp/card.c

pnp_card_intern_scanner = intern_scanner("pnp_card_intern_scanner")

class pnp_card(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'pnp_card',
          tree = tree,
          table_name = 'pnp',
          parent_scanner = parent_scanner,
          struct_name = "pnp_card_device_id",
          struct_fields = ("id", "driver_data", "devs")
          )

    def store(self, dict):
        v0 = extract_string("id", dict)
        if not v0:
            return None
        prods = dict["devs"] ###extract_struct("devs", dict, '{{""}}')
        line = split_structs(prods)[0]
        dict_prod = parse_struct(pnp_card_intern_scanner, unwind_array,
                line, None, None, ret=True)
	vv = tuple(map(lambda n: extract_string(n, dict_prod, ""), unwind_array[:8]))
        return (v0,) + vv


# SERIO , serio_device_id include/linux/mod_devicetable.h drivers/input/serio/serio.c

class serio(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'serio',
          tree = tree,
          table_name = 'serio',
          parent_scanner = parent_scanner,
          struct_name = "serio_device_id",
          struct_fields = ("type", "extra", "id", "proto")
          )

    def store(self, dict):
        v0 = extract_value("type", dict)
        v1 = extract_value("proto", dict)
	if v0 == 0 and v1 == 0:
            return None
        v2 = extract_value("id",dict)
        v3 = extract_value("extra",dict)
	if v1 == 0xff:
	    v1 = -1
	if v2 == 0xff:
	    v2 = -1
	if v3 == 0xff:
	    v3 = -1
        return (v0, v1, v2, v3)


# OF , of_device_id include/linux/mod_devicetable.h

class of(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'of',
          tree = tree,
          table_name = 'of',
          parent_scanner = parent_scanner,
          struct_name = "of_device_id",
          struct_fields = ("name", "type", "compatible", "data")
          )

    def store(self, dict):
        v0 = extract_string("name", dict)
        v1 = extract_string("type", dict)
        v2 = extract_string("compatible", dict)
        if v0 == 0 and v1 == 0 and v2:
            return None
        return (v0, v1, v2)


# VIO , vio_device_id include/linux/mod_devicetable.h

class vio(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'vio',
          tree = tree,
          table_name = 'vio',
          parent_scanner = parent_scanner,
          struct_name = "vio_device_id",
          struct_fields = ("type", "compat")
          )

    def store(self, dict):
        v0 = extract_string("type", dict)
        v1 = extract_string("compat", dict)
        if not v0 and not v1:
            return None
        return (v0, v1)


# PCMCIA , pcmcia_device_id include/linux/mod_devicetable.h drivers/pcmcia/ds.c

pcmcia_intern_scanner = intern_scanner("pcmcia_intern_scanner")

class pcmcia(list_of_structs_scanner):
    PCMCIA_DEV_ID_MATCH_MANF_ID   = 0x0001
    PCMCIA_DEV_ID_MATCH_CARD_ID   = 0x0002
    PCMCIA_DEV_ID_MATCH_FUNC_ID   = 0x0004
    PCMCIA_DEV_ID_MATCH_FUNCTION  = 0x0008
    PCMCIA_DEV_ID_MATCH_PROD_ID1  = 0x0010
    PCMCIA_DEV_ID_MATCH_PROD_ID2  = 0x0020
    PCMCIA_DEV_ID_MATCH_PROD_ID3  = 0x0040
    PCMCIA_DEV_ID_MATCH_PROD_ID4  = 0x0080
    PCMCIA_DEV_ID_MATCH_DEVICE_NO = 0x0100
    PCMCIA_DEV_ID_MATCH_FAKE_CIS  = 0x0200
    PCMCIA_DEV_ID_MATCH_ANONYMOUS = 0x0400

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'pcmcia',
          tree = tree,
          table_name = 'pcmcia',
          parent_scanner = parent_scanner,
          struct_name = "pcmcia_device_id",
          struct_fields = ("match_flags", "manf_id", "card_id", "func_id", "function",
		    "device_no", "prod_id_hash", "prod_id", "driver_info", "cisfile")
          )

    def store(self, dict):
        match = extract_value("match_flags", dict)
        if not match:
            return None
	v0 = -1; v1 = -1; v2 = -1; v3 = -1; v4 = -1
        if match & self.PCMCIA_DEV_ID_MATCH_MANF_ID:
            v0 = extract_value("manf_id", dict)
        if match & self.PCMCIA_DEV_ID_MATCH_CARD_ID:
            v1 = extract_value("card_id", dict)
        if match & self.PCMCIA_DEV_ID_MATCH_FUNC_ID:
            v2 = extract_value("func_id", dict)
        if match & self.PCMCIA_DEV_ID_MATCH_FUNCTION:
            v3 = extract_value("function", dict)
        if match & self.PCMCIA_DEV_ID_MATCH_DEVICE_NO:
            v4 = extract_value("device_no", dict)
	n0, n1, n2, n3 = ("", "", "", "")
	if match & ( self.PCMCIA_DEV_ID_MATCH_PROD_ID1 | self.PCMCIA_DEV_ID_MATCH_PROD_ID2 |
                     self.PCMCIA_DEV_ID_MATCH_PROD_ID3 | self.PCMCIA_DEV_ID_MATCH_PROD_ID4 ):

            prods = dict["prod_id"]
            line = split_structs(prods)[0]
            dict_prod = parse_struct(pcmcia_intern_scanner, unwind_array,
                                                line, None, None, ret=True)
            if match & self.PCMCIA_DEV_ID_MATCH_PROD_ID1:
                n0 = extract_string("n0", dict_prod)
            if match & self.PCMCIA_DEV_ID_MATCH_PROD_ID2:
                n1 = extract_string("n1", dict_prod)
            if match & self.PCMCIA_DEV_ID_MATCH_PROD_ID3:
                n2 = extract_string("n2", dict_prod)
            if match & self.PCMCIA_DEV_ID_MATCH_PROD_ID4:
                n3 = extract_string("n3", dict_prod)
        return (v0, v1, v2, v3, v4,  n0, n1, n2, n3)


# input, input_device_id include/linux/mod_devicetable.h drivers/input/input.c

class input(list_of_structs_scanner):
    INPUT_DEVICE_ID_MATCH_BUS     = 1
    INPUT_DEVICE_ID_MATCH_VENDOR  = 2
    INPUT_DEVICE_ID_MATCH_PRODUCT = 4
    INPUT_DEVICE_ID_MATCH_VERSION = 8
    INPUT_DEVICE_ID_MATCH_EVBIT   = 0x0010
    INPUT_DEVICE_ID_MATCH_KEYBIT  = 0x0020
    INPUT_DEVICE_ID_MATCH_RELBIT  = 0x0040
    INPUT_DEVICE_ID_MATCH_ABSBIT  = 0x0080
    INPUT_DEVICE_ID_MATCH_MSCIT   = 0x0100
    INPUT_DEVICE_ID_MATCH_LEDBIT  = 0x0200
    INPUT_DEVICE_ID_MATCH_SNDBIT  = 0x0400
    INPUT_DEVICE_ID_MATCH_FFBIT   = 0x0800
    INPUT_DEVICE_ID_MATCH_SWBIT   = 0x1000

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'input',
          tree = tree,
          table_name = 'input',
          parent_scanner = parent_scanner,
          struct_name = "input_device_id",
          struct_fields = ("flags", "bustype", "vendor", "product", "version",
		   "evbit", "keybit", "relbit", "absbit", "mscbit", "ledbit",
		   "sndbit", "ffbit", "swbit", "driver_info")
          )

    def store(self, dict):
        match = extract_value("flags", dict)
        if not match:
            return None
	v0 = -1; v1 = -1; v2 = -1; v3 = -1
        if match & self.INPUT_DEVICE_ID_MATCH_BUS:
            v0 = extract_value("bustype", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_VENDOR:
            v1 = extract_value("vendor", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_PRODUCT:
            v2 = extract_value("product", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_VERSION:
            v3 = extract_value("version", dict)
	v4 = -1; v5 = -1; v6 = -1; v7 = -1; v8 = -1;
	v9 = -1; v10 = -1; v11 = -1; v12 = -1;
        if match & self.INPUT_DEVICE_ID_MATCH_EVBIT:
            v4 = extract_value("evbit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_KEYBIT:
            v5 = extract_value("keybit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_RELBIT:
            v6 = extract_value("relbit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_ABSBIT:
            v7 = extract_value("absbit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_MSCIT:
            v8 = extract_value("mscbit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_LEDBIT:
            v9 = extract_value("ledbit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_SNDBIT:
            v10 = extract_value("sndbit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_FFBIT:
            v11 = extract_value("ffbit", dict)
        if match & self.INPUT_DEVICE_ID_MATCH_SWBIT:
            v12 = extract_value("swbit", dict)
	return (v0, v1, v2, v3,  v4, v5, v6, v7, v8, v9, v10, v11, v12)


# EISA, input_device_id include/linux/mod_devicetable.h

class eisa(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'eisa',
          tree = tree,
          table_name = 'eisa',
          parent_scanner = parent_scanner,
          struct_name = "eisa_device_id",
          struct_fields = ("sig", "driver_data")
          )

    def store(self, dict):
        v0 = extract_string("sig", dict)
        if not v0:
            return None
        return (v0,)


# parisc, parisc_device_id include/linux/mod_devicetable.h arch/parisc/kernel/drivers.c

class parisc(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'parisc',
          tree = tree,
          table_name = 'parisc',
          parent_scanner = parent_scanner,
          struct_name = "parisc_device_id",
          struct_fields = ("hw_type", "hversion_rev", "hversion", "sversion")
          )

    def store(self, dict):
        v3 = extract_value("sversion", dict)
	if v3 == 0:
	    return None
        v0 = extract_value("hw_type", dict)
        v1 = extract_value("hversion_rev",dict)
        v2 = extract_value("hversion",dict)
	if v1 == 0xff:
	    v1 = -1
	if v2 == 0xffff:
	    v2 = -1
	if v3 == 0xffffffff:
	    v3 = -1
        return (v0, v1, v2, v3)


# SDIO, sdio_device_id include/linux/mod_devicetable.h drivers/mmc/core/sdio_bus.c

class sdio(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'sdio',
          tree = tree,
          table_name = 'sdio',
          parent_scanner = parent_scanner,
          struct_name = "sdio_device_id",
          struct_fields = ("class", "vendor", "device", "driver_data")
          )

    def store(self, dict):
	v0 = extract_value("class", dict)
        v1 = extract_value("vendor", dict)
        v2 = extract_value("device", dict)
        if v0 == 0  and  v1 == 0  and  c2 == 0:
            return None
        return (v0, v1, v2)


# SSB, sdio_device_id include/linux/mod_devicetable.h drivers/ssb/main.c

class ssb(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'ssb',
          tree = tree,
          table_name = 'ssb',
          parent_scanner = parent_scanner,
          struct_name = "ssb_device_id",
          struct_fields = ("vendor", "coreid", "revision")
          )

    def store(self, dict):
        v0 = extract_value("vendor", dict)
        v1 = extract_value("coreid", dict)
        v2 = extract_value("revision", dict)
        if v0 == 0  and  v1 == 0  and  v2 == 0:
            return None
	if v0 == 0xffff:
	   v0 = -1
	if v1 == 0xffff:
	   v1 = -1
	if v2 == 0xff:
	    v2 = -1
        return (v0, v1, v2)


# virtio, sdio_device_id include/linux/mod_devicetable.h drivers/virtio/virtio.c

class virtio(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'virtio',
          tree = tree,
          table_name = 'virtio',
          parent_scanner = parent_scanner,
          struct_name = "virtio_device_id",
          struct_fields = ("device", "vendor")
          )

    def store(self, dict):
        v0 = extract_value("device", dict)
        v1 = extract_value("vendor", dict)
        if v0 == 0  and  v1 == 0:
            return None
	if v1 == 0xffffffff:
	    v1 = -1
        return (v0, v1)


# I2C i2c_device_id include/linux/mod_devicetable.h i2c_driver include/linux/i2c.h

i2c_intern_scanner = intern_scanner("i2c_intern_scanner")

class i2c(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'i2c',
          tree = tree,
          table_name = 'i2c',
          parent_scanner = parent_scanner,
          struct_name = "i2c_device_id",
          struct_fields = ("name", "driver_data")
          )

    def store(self, dict):
        if not dict.has_key("driver"):
            return None
        block = dict["driver"]
        line = split_structs(block)[0]
        driver_dict = parse_struct(i2c_intern_scanner, device_driver_fields,
                line, None, None, ret=True)
        v0 = extract_value("name", dict)
        return (v0,)


# TC, tc_device_id include/linux/tc.h drivers/tc/tc-driver.c

class tc(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'tc',
          tree = tree,
          table_name = 'tc',
          parent_scanner = parent_scanner,
          struct_name = "tc_device_id",
          struct_fields = ("vendor", "name")
          )

    def store(self, dict):
        v0 = extract_string("vendor", dict)
        v1 = extract_string("name", dict)
        if not v0  and  not v1:
            return None
        return (v0, v1)


# zorro, zorro_device_id include/linux/zorro.h drivers/zorro/zorro-driver.c

class zorro(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'zorro',
          tree = tree,
          table_name = 'zorro',
          parent_scanner = parent_scanner,
          struct_name = "zorro_device_id",
          struct_fields = ("id", "driver_data")
          )

    def store(self, dict):
        id = extract_value("id", dict)
        if id == 0:
            return None
	if id == 0xffffffff:
	    return (-1, -1)
	else:
	    return ( (id >> 16) & 0xffff,  (id & 0xffff) )


# AGP, agp_device_ids drivers/char/agp/agp.h drivers/char/agp/

class agp(list_of_structs_scanner):

    def __init__(self, parent_scanner, tree):
      list_of_structs_scanner.__init__(self,
          name = 'agp',
          tree = tree,
          table_name = 'agp',
          parent_scanner = parent_scanner,
          struct_name = "agp_device_id",
          struct_fields = ("device_id", "chipset", "chipset_name", "chipset_setup")
          )

    def store(self, dict):
        v0 = extract_value("device_id", dict)
	if v0 == 0:
	    return None
        v1 = extract_value("chipset", dict)
        v2 = extract_string("chipset_name", dict)
        return (v0, v1, v2)


