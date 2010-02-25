#: lkddb/sources/linux/__init__.py : scanners for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import register_browser, register_scanner, get_table

# sources
from .kbuild import kver, makefiles, kconfigs
from . import browse_sources
from parse_devicetables import *
from parse_others import *


def register_browsers(kerneldir, dirs):

    # sources
    kver_ = kver(get_table('kver'), kerneldir)
    register_browser(kver_)

    makefiles_ = makefiles(get_table('firmware'), kerneldir, dirs)
    register_browser(makefiles_)

    kconfigs_ = kconfigs(get_table('kconf'), get_table('module'),
				 kerneldir, dirs, makefiles_)
    register_browser(kconfigs_)

    sources_ = browse_sources.linux_sources(kerneldir, dirs)
    register_browser(sources_)

    parent_scanner = browse_sources.struct_parent_scanner(sources_, makefiles_)

    print "stop devicetable scanner, in register_browsers in lkddb/linux/__init__.py"
    return

    # parse_devicetables
    register_scanner(pci(parent_scanner))
    register_scanner(usb(parent_scanner))
    register_scanner(ieee1394(parent_scanner))
    register_scanner(hid(parent_scanner))
    register_scanner(ccw(parent_scanner))
    register_scanner(ap(parent_scanner))
    register_scanner(acpi(parent_scanner))
    register_scanner(pnp(parent_scanner))
    register_scanner(pnp_card(parent_scanner))
    register_scanner(serio(parent_scanner))
    register_scanner(of(parent_scanner))
    register_scanner(vio(parent_scanner))
    register_scanner(pcmcia(parent_scanner))
    register_scanner(input(parent_scanner))
    register_scanner(eisa(parent_scanner))
    register_scanner(parisc(parent_scanner))
    register_scanner(sdio(parent_scanner))
    register_scanner(ssb(parent_scanner))
    register_scanner(virtio(parent_scanner))
    register_scanner(i2c(parent_scanner))
    register_scanner(tc(parent_scanner))
    register_scanner(zorro(parent_scanner))
    register_scanner(agp(parent_scanner))

    # parse_others
    lkddb.register_scanner(i2c_snd(parent_scanner))
    lkddb.register_scanner(platform(parent_scanner))
    lkddb.register_scanner(fs(parent_scanner))

