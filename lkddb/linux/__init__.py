#: lkddb/sources/linux/__init__.py : scanners for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2010  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import os
import subprocess

import lkddb
import lkddb.tables
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
    kver_ = kver(tree.get_table('kver'), tree)
    tree.register_browser(kver_)

    makefiles_ = makefiles(tree.get_table('firmware'), kerneldir, dirs)
    tree.register_browser(makefiles_)

    kconfigs_ = kconfigs(tree.get_table('kconf'), tree.get_table('module'),
				 kerneldir, dirs, makefiles_, tree)
    tree.register_browser(kconfigs_)

    sources_ = browse_sources.linux_sources(kerneldir, dirs)
    tree.register_browser(sources_)

    parent_scanner = browse_sources.struct_parent_scanner(sources_, makefiles_)

    # parse_devicetables
    tree.register_scanner(pci(parent_scanner, tree))
    tree.register_scanner(usb(parent_scanner, tree))
    tree.register_scanner(ieee1394(parent_scanner, tree))
    tree.register_scanner(hid(parent_scanner, tree))
    tree.register_scanner(ccw(parent_scanner, tree))
    tree.register_scanner(ap(parent_scanner, tree))
    tree.register_scanner(acpi(parent_scanner, tree))
    tree.register_scanner(pnp(parent_scanner, tree))
    tree.register_scanner(pnp_card(parent_scanner, tree))
    tree.register_scanner(serio(parent_scanner, tree))
    tree.register_scanner(of(parent_scanner, tree))
    tree.register_scanner(vio(parent_scanner, tree))
    tree.register_scanner(pcmcia(parent_scanner, tree))
    tree.register_scanner(input(parent_scanner, tree))
    tree.register_scanner(eisa(parent_scanner, tree))
    tree.register_scanner(parisc(parent_scanner, tree))
    tree.register_scanner(sdio(parent_scanner, tree))
    tree.register_scanner(ssb(parent_scanner, tree))
    tree.register_scanner(virtio(parent_scanner, tree))
    tree.register_scanner(i2c(parent_scanner, tree))
    tree.register_scanner(tc(parent_scanner, tree))
    tree.register_scanner(zorro(parent_scanner, tree))
    tree.register_scanner(agp(parent_scanner, tree))

    # parse_others
    tree.register_scanner(i2c_snd(parent_scanner, tree))
    tree.register_scanner(platform(parent_scanner, tree))
    tree.register_scanner(fs(parent_scanner, tree))

###

class linux_kernel(lkddb.tree):

    def __init__(self, task, kerneldir, dirs):
        lkddb.tree.__init__(self, "linux-kernel")
	self.kerneldir = kerneldir
	self.dirs = dirs
	lkddb.tables.register_linux_tables(self)
	if task == lkddb.TASK_BUILD:
	    register_browsers(self)

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
            self.isreleased = False
	    self.ishead = True
        else:
            self.isreleased = True
	    self.ishead = False
        self.name = self.dict.get("NAME", '(not named)')

