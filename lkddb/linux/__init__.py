#: lkddb/sources/linux/__init__.py : scanners for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2010  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import os
import subprocess

import lkddb
#from lkddb import register_browser, register_scanner, get_table

# sources
from .kbuild import kver, makefiles, kconfigs
from . import browse_sources
from parse_devicetables import *
from parse_others import *


def register_browsers(tree):

    kerneldir = tree.kerneldir
    dirs = tree.dirs

    # sources
    kver_ = kver(lkddb.get_table('kver'), kerneldir)
    lkddb.register_browser(kver_)

    makefiles_ = makefiles(lkddb.get_table('firmware'), kerneldir, dirs)
    lkddb.register_browser(makefiles_)

    kconfigs_ = kconfigs(lkddb.get_table('kconf'), lkddb.get_table('module'),
				 kerneldir, dirs, makefiles_)
    lkddb.register_browser(kconfigs_)

    sources_ = browse_sources.linux_sources(kerneldir, dirs)
    lkddb.register_browser(sources_)

    parent_scanner = browse_sources.struct_parent_scanner(sources_, makefiles_)

    # parse_devicetables
    lkddb.register_scanner(pci(parent_scanner))
    lkddb.register_scanner(usb(parent_scanner))
    lkddb.register_scanner(ieee1394(parent_scanner))
    lkddb.register_scanner(hid(parent_scanner))
    lkddb.register_scanner(ccw(parent_scanner))
    lkddb.register_scanner(ap(parent_scanner))
    lkddb.register_scanner(acpi(parent_scanner))
    lkddb.register_scanner(pnp(parent_scanner))
    lkddb.register_scanner(pnp_card(parent_scanner))
    lkddb.register_scanner(serio(parent_scanner))
    lkddb.register_scanner(of(parent_scanner))
    lkddb.register_scanner(vio(parent_scanner))
    lkddb.register_scanner(pcmcia(parent_scanner))
    lkddb.register_scanner(input(parent_scanner))
    lkddb.register_scanner(eisa(parent_scanner))
    lkddb.register_scanner(parisc(parent_scanner))
    lkddb.register_scanner(sdio(parent_scanner))
    lkddb.register_scanner(ssb(parent_scanner))
    lkddb.register_scanner(virtio(parent_scanner))
    lkddb.register_scanner(i2c(parent_scanner))
    lkddb.register_scanner(tc(parent_scanner))
    lkddb.register_scanner(zorro(parent_scanner))
    lkddb.register_scanner(agp(parent_scanner))

    # parse_others
    lkddb.register_scanner(i2c_snd(parent_scanner))
    lkddb.register_scanner(platform(parent_scanner))
    lkddb.register_scanner(fs(parent_scanner))


class linux_kernel(lkddb.tree):

    def __init__(self, kerneldir, dirs):
        lkddb.tree.__init__(self, "linux-kernel")
	self.kerneldir = kerneldir
	self.dirs = dirs

    def get_version(self):
	if self.version == None:
	    self.retrive_version()
        return self.version

    def get_strversion(self):
        if self.strversion == None:
            self.retrive_version()
        return self.strversion

    def retrive_version(self):
	"Makefile, scripts/setlocalversion -> return (ver_number, ver_string, released)"
        self.dict = {}
        f = open(os.path.join(self.kerneldir, "Makefile"))
        for i in range(10):
            line = f.readline().strip()
            if not line or line[0] == '#':
                continue
            try:
                label, value = line.split('=', 1)
            except ValueError:
                continue
            self.dict[label.strip()] = value.strip()
        f.close()
        assert(self.dict.has_key("VERSION"))
        assert(self.dict.has_key("PATCHLEVEL"))
        assert(self.dict.has_key("SUBLEVEL"))
        assert(self.dict.has_key("EXTRAVERSION"))

        self.version =  ( int(self.dict["VERSION"])    * 0x10000 +
                         int(self.dict["PATCHLEVEL"]) * 0x100   +
                         int(self.dict["SUBLEVEL"])   )
        self.extra = self.dict["EXTRAVERSION"]
        if self.version == 0x02040f and self.extra == "-greased-turkey":
            self.dict["NAME"] = "greased-turkey"
            self.extra = ""
        self.strversion = self.dict["VERSION"] +"."+ self.dict["PATCHLEVEL"] +"."+ self.dict["SUBLEVEL"] + self.extra

        self.local_ver = subprocess.Popen("/bin/sh scripts/setlocalversion",
                shell=True, cwd=self.kerneldir,
                stdout=subprocess.PIPE).communicate()[0].strip() # .replace("-dirty", "")
        if self.local_ver  or  not self.extra.isdigit():
            # not a x.y.z or x.y.z.w release
            self.strversion += self.local_ver
            self.is_a_release = 1
        else:
            self.is_a_release = 0
        self.name = self.dict.get("NAME", '(not named)')

