#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2000,2001,2007  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import scanners, srcparser
from scanners import value, str_value, mask, chars, strings

# device_driver include/linux/device.h
device_driver_fields = (
    "name", "bus", "kobj", "klist_devices", "knode_bus", "owner", "mod_name",
    "mkobj", "probe", "remove", "shutdown", "suspend", "resume")



class pci(scanners.scanner_array_of_struct):
    "'PCI' pci_device_id include/linux/mod_devicetable.h drivers/pci/pci.h"
    def __init__(self):
	scanners.scanner_array_of_struct.__init__(self,
name          = "pci",
format        = "%s %s %s %s %s", 
db_attrs      = ("vendor", "device", "subvendor", "subdevice", "class"),
struct_name   = "pci_device_id",
struct_fields = ("vendor", "device", "subvendor", "subdevice", "class", "class_mask", "driver_data")
)
    def formatter(self, dict):
        v0 = value("vendor",    dict)
        v1 = value("device",    dict)
        cl = value("class",     dict)
        if v0 == 0  and  v1 == 0  and  cl == 0:
            return None
        v2 = value("subvendor", dict)
        v3 = value("subdevice", dict)
        cm = value("class_mask",dict)
	v0 = str_value(v0, -1, 4)
        v1 = str_value(v1, -1, 4)
        v2 = str_value(v2, -1, 4)
        v3 = str_value(v3, -1, 4)
        cl = str_value(cl, -1, 6).replace("......", "ffffff") ### really needed ?????????
        cm = str_value(cm, -1, 6).replace("......", "ffffff")
        v4 = mask(cl, cm, 6)
        return (v0, v1, v2, v3, v4)

scanners.register_scanner(pci())



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

class usb(scanners.scanner_array_of_struct):
    "'USB' usb_device_id include/linux/mod_devicetable.h drivers/usb/core/driver.c"
    def __init__(self):
	scanners.scanner_array_of_struct.__init__(self,
name          = "usb",
format        = "%s %s %s%s%s %s%s%s %s %s",
db_attrs      = ("idVendor", "idProduct", "bDeviceClass","bDeviceSubClass","bDeviceProtocol",
    "bInterfaceClass","bInterfaceSubClass","bInterfaceProtocol","bcdDevice_lo","bcdDevice_hi"),
struct_name   = "usb_device_id",
struct_fields = ("match_flags", "idVendor", "idProduct", "bcdDevice_lo", "bcdDevice_hi",
    "bDeviceClass", "bDeviceSubClass", "bDeviceProtocol",
    "bInterfaceClass", "bInterfaceSubClass", "bInterfaceProtocol",
    "driver_info")
)
    def formatter(self, dict):
    	match = value("match_flags", dict)
        if not match:
            return None
        v0 = "...." ; v1 = "...."
        v2 = "0000"
        v3 = "ffff"
        v4 = ".." ; v5 = ".." ; v6 = ".."
        v7 = ".." ; v8 = ".." ; v9 = ".."
        if match & USB_DEVICE_ID_MATCH_VENDOR:
            v0 = str_value(value("idVendor", dict), -1, 4)
        if match & USB_DEVICE_ID_MATCH_PRODUCT:
            v1 = str_value(value("idProduct", dict), -1, 4)
        if match & USB_DEVICE_ID_MATCH_DEV_LO:
            v2 = str_value(value("bcdDevice_lo", dict), -1, 4)
        if match & USB_DEVICE_ID_MATCH_DEV_HI:
            v3 = str_value(value("bcdDevice_hi", dict), -1, 4)
        if match & USB_DEVICE_ID_MATCH_DEV_CLASS:
            v4 = str_value(value("bDeviceClass", dict), -1, 2)
        if match & USB_DEVICE_ID_MATCH_DEV_SUBCLASS:
            v5 = str_value(value("bDeviceSubClass", dict), -1, 2)
        if match & USB_DEVICE_ID_MATCH_DEV_PROTOCOL:
            v6 = str_value(value("bDeviceProtocol", dict), -1, 2)
        if match & USB_DEVICE_ID_MATCH_INT_CLASS:
            v7 = str_value(value("bInterfaceClass", dict), -1, 2)
        if match & USB_DEVICE_ID_MATCH_INT_SUBCLASS:
            v8 = str_value(value("bInterfaceSubClass", dict), -1, 2)
        if match & USB_DEVICE_ID_MATCH_INT_PROTOCOL:
            v9 = str_value(value("bInterfaceProtocol", dict), -1, 2)
        return (v0, v1, v4,v5,v6, v7,v8,v9, v2, v3)

scanners.register_scanner(usb())



IEEE1394_MATCH_VENDOR_ID    = 0x0001
IEEE1394_MATCH_MODEL_ID     = 0x0002
IEEE1394_MATCH_SPECIFIER_ID = 0x0004
IEEE1394_MATCH_VERSION      = 0x0008

class ieee1394(scanners.scanner_array_of_struct):
    "'IEEE1394' ieee1394_device_id include/linux/mod_devicetable.h ?"
    def __init__(self):
	scanners.scanner_array_of_struct.__init__(self,
name          = "ieee1394",
format        = "%s %s %s %s",
db_attrs      = ("vendor_id", "model_id", "specifier_id", "version"),
struct_name   = "ieee1394_device_id",
struct_fields = ("match_flags", "vendor_id", "model_id", "specifier_id", "version", "driver_data")
)
    def formatter(self, dict):
        match = value("match_flags", dict)
        if not match:
            return
        v0 = "......" ; v1 = "......"
        v2 = "......" ; v3 = "......"
        if match & IEEE1394_MATCH_VENDOR_ID:
            v0 = str_value(value("vendor_id", dict), -1, 6)
        if match & IEEE1394_MATCH_MODEL_ID:
            v1 = str_value(value("model_id", dict), -1 , 6)
        if match & IEEE1394_MATCH_SPECIFIER_ID:
            v2 = str_value(value("specifier_id", dict), -1, 6)
        if match & IEEE1394_MATCH_VERSION:
            v3 = str_value(value("version", dict), -1, 6)
        return (v0, v1, v2, v3)

scanners.register_scanner(ieee1394())



class hid(scanners.scanner_array_of_struct):
    "'HID' hid_device_id include/linux/mod_devicetable.h"
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "hid",
format        = "%s %s %s",
db_attrs      = ("bus", "vendor", "product"),
struct_name   = "hid_device_id",
struct_fields = ("bus", "vendor", "product", "driver_data"))
    def formatter(self, dict):
        v0 = value("bus",     dict)
        v1 = value("vendor",  dict)
        v2 = value("product", dict)
        if v0 == 0  and  v1 == 0  and  v2 == 0:
            return None
        v0 = str_value(v0, -1, 4)
        v1 = str_value(v1, -1, 8)
        v2 = str_value(v2, -1, 8)
        return (v0, v1, v2)

scanners.register_scanner(hid())



CCW_DEVICE_ID_MATCH_CU_TYPE      = 0x01
CCW_DEVICE_ID_MATCH_CU_MODEL     = 0x02
CCW_DEVICE_ID_MATCH_DEVICE_TYPE  = 0x04
CCW_DEVICE_ID_MATCH_DEVICE_MODEL = 0x08

class ccw(scanners.scanner_array_of_struct):
    "s390 CCW ccw_device_id include/linux/mod_devicetable.h"
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "ccw",
format        = "%s %s %s %s",
db_attrs      = ("cu_type","cu_model","dev_type","dev_model"),
struct_name   = "ccw_device_id",
struct_fields =("match_flags", "cu_type", "dev_type", "cu_model", "dev_model", "driver_info")
)
    def formatter(self, dict):
        try:
            match = value("match_flags", dict)
        except:
            return
        if not match:
            return
        v0 = "...." ; v1 = ".."
        v2 = "...." ; v3 = ".."
        if match & CCW_DEVICE_ID_MATCH_CU_TYPE:
            v0 = str_value(value("cu_type", dict), -1, 4)
        if match & CCW_DEVICE_ID_MATCH_CU_MODEL:
            v1 = str_value(value("cu_model", dict), -1, 2)
        if match & CCW_DEVICE_ID_MATCH_DEVICE_TYPE:
            v2 = str_value(value("dev_type", dict), -1, 4)
        if match & CCW_DEVICE_ID_MATCH_DEVICE_MODEL:
            v3 = str_value(value("dev_model", dict), -1, 2)
        return (v0, v1, v2, v3)

scanners.register_scanner(ccw())



# s390 AP bus devices ap_device_id include/linux/mod_devicetable.h
AP_DEVICE_ID_MATCH_DEVICE_TYPE = 0x01

class ap(scanners.scanner_array_of_struct):
    "'s390 AP bus devices' ap_device_id include/linux/mod_devicetable.h"
    def __init__(self):
	scanners.scanner_array_of_struct.__init__(self,
name          = "ap",
format        = "%s",
db_attrs      = ("dev_type",),
struct_name   = "ap_device_id",
struct_fields = ("match_flags", "dev_type", "pad1", "pad2", "driver_info")
)
    def formatter(self, dict):
        match = value("match_flags", dict)
        if not match:
            return
        if match & AP_DEVICE_ID_MATCH_DEVICE_TYPE:
            v0 = str_value(value("dev_type",   dict), -1, 2)
        else:
            v0 = ".."
        return (v0,)

scanners.register_scanner(ap())



# ACPI , acpi_device_id include/linux/mod_devicetable.h drivers/acpi/scan.c

class acpi(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "acpi",
format        = "%s",
db_attrs      = ("id",),
struct_name   = "acpi_device_id",
struct_fields =("id", "driver_data")
)
    def formatter(self, dict):
        v0 = strings("id",   dict, '""')
        if v0 == '""':
            return None
        return (v0,)

scanners.register_scanner(acpi())



# PNP #1, pnp_device_id include/linux/mod_devicetable.h drivers/pnp/driver.c

class pnp(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "pnp",
format        = "%s",
db_attrs      = ("id",),
struct_name   = "pnp_device_id",
struct_fields = ("id", "driver_data")
)
    def formatter(self, dict):
        v0 = strings("id",   dict, '""')
        if v0 == '""':
            return None
        return (v0,)

scanners.register_scanner(pnp())



# PNP #2, pnp_card_device_id include/linux/mod_devicetable.h drivers/pnp/card.c

class pnp_card(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "pnp_card",
format        = "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s",
db_attrs      = ("id", "n0", "n1","n2","n3","n4","n5","n6","n7"),
struct_name   = "pnp_card_device_id",
struct_fields = ("id", "driver_data", "devs")
)
    def formatter(self, dict):
        v0 = strings("id",   dict, '""')
        if v0 == '""':
            return
        s = ['"......."',]*8
        prods = scanners.nullstring_re.sub('""', dict["devs"])
        line = scanners.split_structs(prods)[0]
        dict_prod = srcparser.parse_struct(None, scanners.unwind_array,
		line, None, None, ret=True)
        for i in range(8):
            s[i] = strings("n%u"%(i+1), dict_prod, '""')
	return (v0, s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7])

scanners.register_scanner(pnp_card())



# SERIO , serio_device_id include/linux/mod_devicetable.h drivers/input/serio/serio.c

class serio(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "serio",
format        = "%s %s %s %s",
db_attrs      = ("type", "extra", "id", "proto"),
struct_name   = "serio_device_id",
struct_fields = ("type", "extra", "id", "proto")
)
    def formatter(self, dict):
        v0 = value("type", dict)
        v1 = value("proto", dict)
        if v0 == 0  and  v1 == 0:
            return
        v0 = str_value(v0, 0xff, 2)
        v1 = str_value(v1, 0xff, 2)
        v2 = str_value(value("id", dict), 0xff, 2)
        v3 = str_value(value("extra", dict), 0xff, 2)
	return (v0, v1, v2, v3)

scanners.register_scanner(serio())



# OF , of_device_id include/linux/mod_devicetable.h

class of(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "of",
format        = "%s\t%s\t%s",
db_attrs      = ("name", "type", "compatible"),
struct_name   = "of_device_id",
struct_fields = ("name", "type", "compatible", "data")
)
    def formatter(self, dict):
        v0 = strings("name",   dict, '""')
        v1 = strings("type",   dict, '""')
        v2 = strings("compat", dict, '""')
        if v0 == '""'  and  v1 == '""'  and  v2 == '""':
            return None
        return (v0, v1, v2)

scanners.register_scanner(of())



# VIO , vio_device_id include/linux/mod_devicetable.h

class vio(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "vio",
format        = "%s\t%s",
db_attrs      = ("type", "compat"),
struct_name   = "vio_device_id",
struct_fields = ("type", "compat")
)
    def formatter(self, dict):
        v0 = strings("type",   dict, '""')
        v1 = strings("compat", dict, '""')
        if v0 == '""'  and  v1 == '""':
            return None
	return (v0, v1)

scanners.register_scanner(vio())



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

# PCMCIA , pcmcia_device_id include/linux/mod_devicetable.h drivers/pcmcia/ds.c

class pcmcia(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "pcmcia",
format        = "%s %s %s %s %s\t%s\t%s\t%s\t%s",
db_attrs      = ("manf_id", "card_id", "func_id", "function", "device_no", "n1", "n2", "n3", "n4"),
struct_name   = "pcmcia_device_id",
struct_fields = ("match_flags", "manf_id", "card_id", "func_id", "function",
    "device_no", "prod_id_hash", "prod_id", "driver_info", "cisfile")
)
    def formatter(self, dict):
        match = value("match_flags", dict)
        if not match:
            return None
        v0 = "...."  ;  v1 = "...."
        v2 = ".."  ;  v3 = ".."  ;  v4 = ".."
        if match & PCMCIA_DEV_ID_MATCH_MANF_ID:
            v0 = str_value(value("manf_id", dict), -1, 4)
        if match & PCMCIA_DEV_ID_MATCH_CARD_ID:
            v1 = str_value(value("card_id", dict), -1, 4)
        if match & PCMCIA_DEV_ID_MATCH_FUNC_ID:
            v2 = str_value(value("func_id", dict), -1, 2)
        if match & PCMCIA_DEV_ID_MATCH_FUNCTION:
            v3 = str_value(value("function", dict), -1, 2)
        if match & PCMCIA_DEV_ID_MATCH_DEVICE_NO:
            v4 = str_value(value("device_no", dict), -1, 2)
        s1 = '""' ; s2 = '""'; s3 = '""' ;  s4 = '""'
        if match & ( PCMCIA_DEV_ID_MATCH_PROD_ID1 | PCMCIA_DEV_ID_MATCH_PROD_ID2 |
                     PCMCIA_DEV_ID_MATCH_PROD_ID3 | PCMCIA_DEV_ID_MATCH_PROD_ID4 ):
            prods = scanners.nullstring_re.sub('""', dict["prod_id"])
            line = scanners.split_structs(prods)[0]
            dict_prod = srcparser.parse_struct(None, scanners.unwind_array,
						line, None, None, ret=True)
            if match | PCMCIA_DEV_ID_MATCH_PROD_ID1:
                s1 = strings("n1", dict_prod, '""')
            if match | PCMCIA_DEV_ID_MATCH_PROD_ID2:
                s2 = strings("n2", dict_prod, '""')
            if match | PCMCIA_DEV_ID_MATCH_PROD_ID3:
                s3 = strings("n3", dict_prod, '""')
            if match | PCMCIA_DEV_ID_MATCH_PROD_ID4:
                s4 = strings("n4", dict_prod, '""')
	return (v0, v1, v2, v3, v4, s1, s2, s3, s4)

scanners.register_scanner(pcmcia())



# input, input_device_id include/linux/mod_devicetable.h drivers/input/input.c
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

class input(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "input",
format        = "%s %s %s %s\t%s %s %s %s %s %s %s %s %s",
db_attrs      = ("bustype", "vendor", "product", "version",
    "evbit", "keybit", "relbit", "absbit", "mscbit", "ledbit", "sndbit", "ffbit", "swbit"),
struct_name   = "input_device_id",
struct_fields = ("flags", "bustype", "vendor", "product", "version",
   "evbit", "keybit", "relbit", "absbit", "mscbit", "ledbit", "sndbit", "ffbit", "swbit",
   "driver_info")
)
    def formatter(self, dict):
        match = value("flags", dict)
        if not match:
            return
        v0 = "...."  ;  v1 = "...."
        v2 = "...."  ;  v3 = "...."
        if match & INPUT_DEVICE_ID_MATCH_BUS:
            v0 = str_value(value("bustype", dict), -1, 4)
        if match & INPUT_DEVICE_ID_MATCH_VENDOR:
            v1 = str_value(value("vendor",  dict), -1, 4)
        if match & INPUT_DEVICE_ID_MATCH_PRODUCT:
            v2 = str_value(value("product", dict), -1, 4)
        if match & INPUT_DEVICE_ID_MATCH_VERSION:
            v3 = str_value(value("version", dict), -1, 4)
        b1 = "ff"
        b2 = "ffff"
        b3 = "ff"  ;  b4 = "ff"  ;  b5 = "ff"
        b6 = "ff"  ;  b7 = "ff"  ;  b8 = "ff"
        b9 = "ff"
        if match & INPUT_DEVICE_ID_MATCH_EVBIT:
            b1 = str_value(value("evbit",  dict), -1, 2)
        if match & INPUT_DEVICE_ID_MATCH_KEYBIT:
            b2 = str_value(value("keybit", dict), -1, 4)
        if match & INPUT_DEVICE_ID_MATCH_RELBIT:
            b3 = str_value(value("relbit", dict), -1, 2)
        if match & INPUT_DEVICE_ID_MATCH_ABSBIT:
            b4 = str_value(value("absbit", dict), -1, 2)
        if match & INPUT_DEVICE_ID_MATCH_MSCIT:
            b5 = str_value(value("mscbit", dict), -1, 2)
        if match & INPUT_DEVICE_ID_MATCH_LEDBIT:
            b6 = str_value(value("ledbit", dict), -1, 2)
        if match & INPUT_DEVICE_ID_MATCH_SNDBIT:
            b7 = str_value(value("sndbit", dict), -1, 2)
        if match & INPUT_DEVICE_ID_MATCH_FFBIT:
            b8 = str_value(value("ffbit",  dict), -1, 2)
        if match & INPUT_DEVICE_ID_MATCH_SWBIT:
            b9 = str_value(value("swbit",  dict), -1, 2)
        return (v0, v1, v2, v3, b1, b2, b3, b4, b5, b6, b7, b8, b9)

scanners.register_scanner(input())



# EISA, input_device_id include/linux/mod_devicetable.h 

class eisa(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "eisa",
format        = "%s",
db_attrs      = ("sig",),
struct_name   = "eisa_device_id",
struct_fields = ("sig", "driver_data")
)
    def formatter(self, dict):
        v0 = strings("sig", dict, '""')
        if v0 == '""':
            return
        return (v0,)

scanners.register_scanner(eisa())



# parisc, parisc_device_id include/linux/mod_devicetable.h arch/parisc/kernel/drivers.c

class parisc(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "parisc",
format        = "%s %s %s %s",
db_attrs      = ("hw_type", "hversion_rev", "hversion", "sversion"),
struct_name   = "parisc_device_id",
struct_fields = ("hw_type", "hversion_rev", "hversion", "sversion")
)
    def formatter(self, dict):
        v3 = value("sversion", dict)
        if v3 == 0:
            return
        v3 = str_value(v3, 0xffffffff, 8)
        v0 = str_value(value("hw_type", dict), 0xff, 2)
        v1 = str_value(value("hversion_rev", dict), 0xff, 2)
        v2 = str_value(value("hversion", dict), 0xffff, 4)
        return (v0, v1, v2, v3)

scanners.register_scanner(parisc())


# SDIO, sdio_device_id include/linux/mod_devicetable.h drivers/mmc/core/sdio_bus.c 

class sdio(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "sdio",
format        = "%s %s %s",
db_attrs      = ("class", "vendor", "device"),
struct_name   = "sdio_device_id",
struct_fields = ("class", "vendor", "device", "driver_data")
)
    def formatter(self, dict):
        v0 = value("class",  dict)
        v1 = value("vendor", dict)
        v2 = value("device", dict)
        if v0 == 0  and  v1 == 0  and  v2 == 0:
            return
        v0 = str_value(v0, -1, 2)
        v1 = str_value(v1, -1, 4)
        v2 = str_value(v2, -1, 4)
        return (v0, v1, v2)

scanners.register_scanner(sdio())



# SBB, sdio_device_id include/linux/mod_devicetable.h drivers/ssb/main.c

class sbb(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "sbb",
format        = "%s %s %s",
db_attrs      = ("vendor", "coreid", "revision"),
struct_name   = "ssb_device_id",
struct_fields = ("vendor", "coreid", "revision")
)
    def formatter(self, dict):
        v0 = value("vendor",  dict)
        v1 = value("coreid",  dict)
        v2 = value("revision",dict)
        if v0 == 0  and  v1 == 0  and  v2 == 0:
            return
        v0 = str_value(v0, 0xffff, 4)
        v1 = str_value(v1, 0xffff, 4)
        v2 = str_value(v2, 0xff,   2)
        return (v0, v1, v2)

scanners.register_scanner(sbb())



# virtio, sdio_device_id include/linux/mod_devicetable.h drivers/virtio/virtio.c

class virtio(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "virtio",
format        = "%s %s",
db_attrs      = ("device", "vendor"),
struct_name   = "virtio_device_id",
struct_fields = ("device", "vendor")
)
    def formatter(self, dict):
        v0 = value("device", dict)
        v1 = value("vendor", dict)
        if v0 == 0  and  v1 == 0:
            return
        v0 = str_value(v0, -1, 8)
        v1 = str_value(v1, 0xffffffff, 8)
        return (v0, v1)

scanners.register_scanner(virtio())



# I2C i2c_device_id include/linux/mod_devicetable.h i2c_driver include/linux/i2c.h

class i2c(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "i2c",
format        = "%s",
db_attrs      = ("name",),
struct_name   = "i2c_driver",
struct_fields = ("name", "driver_data")
)
    def formatter(self, dict):
        if not dict.has_key("driver"):
            return
        block = dict["driver"]
        line = scanners.split_structs(block)[0]
        driver_dict = srcparser.parse_struct(None, device_driver_fields,
		line, None, None, ret=True)
        v0 = strings("name", driver_dict, '""')
        return (v0,)

scanners.register_scanner(i2c())



# TC, tc_device_id include/linux/tc.h drivers/tc/tc-driver.c

class tc(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "tc",
format        = "%s\t%s",
db_attrs      = ("vendor", "name"),
struct_name   = "tc_device_id",
struct_fields = ("vendor", "name")
)
    def formatter(self, dict):
        v0 = strings("vendor", dict, '""')
        v1 = strings("name", dict, '""')
        if v0 == '""'  and  v1 == '""':
            return
        return (v0, v1)

scanners.register_scanner(tc())



# zorro, zorro_device_id include/linux/zorro.h drivers/zorro/zorro-driver.c

class zorro(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "zorro",
format        = "%s %s",
db_attrs      = ("id1", "id2"),
struct_name   = "zorro_device_id",
struct_fields = ("id", "driver_data")
)
    def formatter(self, dict):
        v0 = value("id", dict)
        if v0 == 0:
	    return
        v0 = str_value(v0, 0xffffffff, 8)
        v1 = v0[0:4]
        v2 = v0[4:8]
        return (v1, v2)

scanners.register_scanner(zorro())



# AGP, agp_device_ids drivers/char/agp/agp.h drivers/char/agp/

class agp(scanners.scanner_array_of_struct):
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
name          = "agp",
format        = "xxxx %s\t%s",
db_attrs      = ("chipset", "chipset_name"),
struct_name   = "agp_device_ids",
struct_fields = ("device_id", "chipset", "chipset_name", "chipset_setup")
)
    def formatter(self, dict):
        v1 = value("id", dict)
        if v1 == 0:
            return
        v1 = str_value(v1, 0xffff, 4)
        v2 = strings("chipset_name", dict, '""')
        return (v0, v1, v2)

scanners.register_scanner(agp())


# I2C , i2c_driver include/linux/i2c.h
ifdef0 = """
i2c_old = utils.scanner_struct
    def __init__(self):
        scanners.scanner_array_of_struct.__init__(self,
"i2c", "i2c\t%s",
("name",),
"i2c_driver",
("id", "class", "attach_adapter", "detach_adapter", "detach_client",
   "probe", "remove", "shutdown", "suspend", "resume", "command",
   "driver", "list"))
    def formatter(self, dict):
        if not dict.has_key("driver"):
	    return
        block = dict["driver"]
        line = utils.split_structs(block)[0]
        driver_dict =  utils.parse_struct(None, device_driver_fields, line, None, filename, ret=True)
        v0 = strings("name", driver_dict, '""')
        return (v0,)

scanners.register_scanner(i2c())
"""

# I2C snd , snd_i2c_device_create sound/i2c/i2c.c

class i2c_snd(scanners.scanner_funct):
    def __init__(self):
        scanners.scanner_funct.__init__(self,
name          = "i2c_snd",
format        = "%s",
db_attrs      = ("name",),
funct_name    = "snd_i2c_device_create",
funct_args    = ("bus", "name", "addr", "rdevice"))
    def formatter(self, dict):
        if not dict.has_key("name"):
            return
        v0 = strings("name", dict, '""')
        return (v0,)

scanners.register_scanner(i2c_snd())


# "platform" , platform_driver include/linux/platform_device.h

class platform(scanners.scanner_struct):
    def __init__(self):
        scanners.scanner_struct.__init__(self,
name          = "platform",
format        = "%s",
db_attrs      = ("name",),
struct_name   = "platform_driver",
struct_fields = ("probe", "remove", "shutdown", "suspend_late", "resume_early",
   "suspend", "resume", "driver")
)
    def formatter(self, dict):
        if not dict.has_key("driver"):
            return
        block = dict["driver"]
        line = scanners.split_structs(block)[0]
        driver_dict = srcparser.parse_struct(None, device_driver_fields, line, None, None, ret=True)
        v0 = strings("name", driver_dict, '""')
        return (v0,)

scanners.register_scanner(platform())


# fs , file_system_type include/linux/fs.h


class fs(scanners.scanner_struct):
    def __init__(self):
        scanners.scanner_struct.__init__(self,
name          = "fs",
format        = "%s",
db_attrs      = ("name",),
struct_name   = "file_system_type",
struct_fields = ("name", "fs_flags", "get_sb", "kill_sb", "owner", "next", "fs_supers",
  "s_lock_key", "s_umount_key", "i_lock_key", "i_mutex_key",
  "i_mutex_dir_key", "i_alloc_sem_key")
)
    def formatter(self, dict):
        v0 = strings("name", dict, '""')
        return (v0,)

scanners.register_scanner(fs())



# other scanners (non actives)

class module(scanners.scanner):
    def __init__(self):
        scanners.scanner.__init__(self,
name          = "module",
format        = '%s\t"%s"',
db_attrs      = ("name", "descr"),
regex	      = r'^config\s*(\w+)\s+tristate\s+"(.*?[^\\])"',
struct_fields = ("name", "descr")
)
    def formatter(self, dict):
        return (dict['name'], dict['descr'])

module_scanner = module()
scanners.register_scanner(module_scanner, type=scanners.other_scanners)

