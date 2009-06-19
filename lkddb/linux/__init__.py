#: lkddb/sources/linux/__init__.py : scanners for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import register_browser, register_scanner, get_table

# sources
from .kbuild import kver, makefiles, kconfigs
from . import sources, devicetables
# tables
#from . import tables_build

def register_browsers(kerneldir, dirs):

    # sources
    kver_ = kver(get_table('kver'), kerneldir)
    register_browser(kver_)

    makefiles_ = makefiles(kerneldir, dirs)
    register_browser(makefiles_)

    kconfigs_ = kconfigs(get_table('kconf'),
			 get_table('module'), kerneldir, dirs, makefiles_)
    register_browser(kconfigs_)

    sources_ = sources.linux_sources(kerneldir, dirs)
    register_browser(sources_)

    # devices if not done at sources level (directly or indirectly)
    parent_scanner = sources.struct_parent_scanner(sources_, makefiles_)
    register_scanner(devicetables.pci(parent_scanner))
    register_scanner(devicetables.usb(parent_scanner))
    register_scanner(devicetables.ieee1394(parent_scanner))
#    register_scanner(devicetables.hid(parent_scanner))
#    register_scanner(devicetables.ccw(parent_scanner))
#    register_scanner(devicetables.ap(parent_scanner))
#    register_scanner(devicetables.acpi(parent_scanner))
#    register_scanner(devicetables.pnp(parent_scanner))
#    register_scanner(devicetables.pnp_card(parent_scanner))
#    register_scanner(devicetables.serio(parent_scanner))
#    register_scanner(devicetables.of(parent_scanner))
#    lkddb.register_scanner(devicetables.vio(parent_scanner))
#    lkddb.register_scanner(devicetables.pcmcia(parent_scanner))
#    lkddb.register_scanner(devicetables.input(parent_scanner))
#    lkddb.register_scanner(devicetables.eisa(parent_scanner))
#    lkddb.register_scanner(devicetables.parisc(parent_scanner))
#    lkddb.register_scanner(devicetables.sdio(parent_scanner))
#    lkddb.register_scanner(devicetables.sbb(parent_scanner))
#    lkddb.register_scanner(devicetables.virtio(parent_scanner))
#    lkddb.register_scanner(devicetables.i2c(parent_scanner))
#    lkddb.register_scanner(devicetables.tc(parent_scanner))

#    lkddb.register_scanner(devicetables.(parent_scanner))
#    lkddb.register_scanner(devicetables.(parent_scanner))
#    lkddb.register_scanner(devicetables.(parent_scanner))
#    lkddb.register_scanner(devicetables.(parent_scanner))
#    lkddb.register_scanner(devicetables.(parent_scanner))
#    lkddb.register_scanner(devicetables.(parent_scanner))
#    lkddb.register_scanner(devicetables.(parent_scanner))
#    lkddb.register_scanner(devicetables.(parent_scanner))

