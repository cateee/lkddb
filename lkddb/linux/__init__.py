#!/usr/bin/python
#: lkddb/linux/__init__.py : scanners for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import logging
import os
import os.path
import subprocess

import lkddb

logger = logging.getLogger(__name__)

tables = {}

scanners = {}


# sources

def register_linux_browsers(tree):
    # TODO: later we should put the import again on top level
    # for now we keep there to avoid loop on import (refactoring)
    from . import kbuild
    from . import browse_sources
    from . import parse_devicetables
    from . import parse_others

    import lkddb.tables.linux_devicetables
    import lkddb.tables.linux_kbuild
    import lkddb.tables.linux_others

    kerneldir = tree.kerneldir
    dirs = tree.dirs

    # sources
    kver_ = kbuild.Kver(tree.get_table('kver'), tree)
    tree.register_browser(kver_)

    makefiles_ = kbuild.Makefiles(tree.get_table('firmware'), kerneldir, dirs)
    tree.register_browser(makefiles_)

    kconfigs_ = kbuild.Kconfigs(tree.get_table('kconf'), tree.get_table('module'), kerneldir, dirs, makefiles_, tree)
    tree.register_browser(kconfigs_)

    sources_ = browse_sources.LinuxKernelBrowser(kerneldir, dirs)
    tree.register_browser(sources_)

    parent_scanner = browse_sources.struct_parent_scanner(sources_, makefiles_)

    # parse_devicetables
    tree.register_scanner(parse_devicetables.pci(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.usb(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.ieee1394(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.hid(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.ccw(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.ap(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.acpi(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.pnp(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.pnp_card(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.serio(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.hda(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.sdw(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.of(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.vio(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.pcmcia(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.input(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.eisa(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.parisc(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.sdio(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.ssb(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.bcma(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.virtio(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.rpmsg(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.i2c(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.pci_epf(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.i3c(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.spi(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.slim(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.apr(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.spmi(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.tc(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.zorro(parent_scanner, tree))
    tree.register_scanner(parse_devicetables.agp(parent_scanner, tree))

    # parse_others
    tree.register_scanner(parse_others.i2c_snd(parent_scanner, tree))
    tree.register_scanner(parse_others.platform(parent_scanner, tree))
    tree.register_scanner(parse_others.fs(parent_scanner, tree))


###

def numeric_kernel_version(version, patchlevel, sublevel):
    return version << 16 + patchlevel << 8 + sublevel


class LinuxKernelTree(lkddb.Tree):

    def __init__(self, task, kerneldir, dirs):
        super().__init__("linux-kernel", tables)
        self.kerneldir = kerneldir
        self.dirs = dirs
        if task == lkddb.TASK_BUILD:
            self.retrieve_version()
        if task == lkddb.TASK_BUILD:
            register_linux_browsers(self)

    def retrieve_version(self):
        """Makefile, scripts/setlocalversion -> return (ver_number, ver_string, released)"""
        version_dict = {}
        f = open(os.path.join(self.kerneldir, "Makefile"))
        for i in range(10):
            line = f.readline().strip()
            if not line or line[0] == '#':
                continue
            try:
                label, value = line.split('=', 1)
            except ValueError:
                continue
            version_dict[label.strip()] = value.strip()
        f.close()
        assert("VERSION" in version_dict)
        assert("PATCHLEVEL" in version_dict)
        assert("SUBLEVEL" in version_dict)
        assert("EXTRAVERSION" in version_dict)

        version_dict['version'] = int(version_dict["VERSION"])
        version_dict['patchlevel'] = int(version_dict["PATCHLEVEL"])
        version_dict['sublevel'] = int(version_dict["SUBLEVEL"])

        version_dict['numeric'] = (version_dict["version"] * 0x10000 +
                                   version_dict["patchlevel"] * 0x100 +
                                   version_dict["sublevel"])
        version_dict['extra'] = version_dict["EXTRAVERSION"]
        if version_dict['numeric'] == (numeric_kernel_version(2, 4, 15) and
                                       version_dict['extra'] == "-greased-turkey"):
            version_dict["name"] = "greased-turkey"
            version_dict['extra'] = ""
        else:
            version_dict["name"] = version_dict.get("NAME", "")
        if version_dict["VERSION"] >= "3" and version_dict["SUBLEVEL"] == "0":
            # 3.x versions
            version_dict['str'] = version_dict["VERSION"] + "." + version_dict["PATCHLEVEL"] + version_dict['extra']
        else:
            version_dict['str'] = (version_dict["VERSION"] + "." + version_dict["PATCHLEVEL"] +
                                   "." + version_dict["SUBLEVEL"] + version_dict['extra'])
        extra = version_dict['extra']
        if not extra:
            version_dict['numeric2'] = 0
        elif extra.isdigit():
            version_dict['numeric2'] = int(extra)
        elif version_dict['extra'].startswith("-rc") and extra[3:].isdigit():
            version_dict['numeric2'] = -0x100 + int(extra[3:])
        elif extra.startswith("-pre") and extra[4:].isdigit():
            version_dict['numeric2'] = -0x200 + int(extra[4:])
        elif extra.startswith("pre") and extra[3:].isdigit():
            version_dict['numeric2'] = -0x200 + int(extra[3:])
        else:
            assert False, "Unknown structure of EXTRAVERSION (%s) in kernel version" % extra

        if os.path.exists(os.path.join(self.kerneldir, "scripts/setlocalversion")):
            f = open(os.path.join(self.kerneldir, "scripts/setlocalversion"))
            bang = f.readline()
            if bang.startswith("#!"):
                bang = bang[2:].strip()
                script = subprocess.Popen(bang + " scripts/setlocalversion .",
                                          shell=True, cwd=self.kerneldir, stdout=subprocess.PIPE)
                version_dict['local_ver'] = (
                    script.communicate()[0].decode('utf-8', 'replace').strip().replace("-dirty", ""))
                if script.returncode > 0:
                    version_dict['local_ver'] = ""
        else:
            version_dict['local_ver'] = ""
        if not version_dict['local_ver'] or version_dict['local_ver'] == '-dirty':
            version_dict['numeric3'] = 0
        elif (version_dict['local_ver'][0] == '-' and version_dict['local_ver'][6] == '-' and
              version_dict['local_ver'][1:6].isdigit()):
            version_dict['numeric3'] = int(version_dict['local_ver'][1:6])
        elif version_dict['numeric'] <= numeric_kernel_version(2, 6, 15):
            version_dict['numeric3'] = 0
        else:
            assert False, ("Unknown structure of scripts/setlocalversion (%s) in kernel version" %
                           version_dict["local_ver"])

        if version_dict['numeric3'] == 0 and version_dict['numeric2'] == 0:
            # a x.y or x.y.z or x.y.z.w release
            version_dict['serie'] = 1
        else:
            # not a x.y, x.y.z or x.y.z.w release
            version_dict['str'] += version_dict['local_ver']
            version_dict['serie'] = -1
        self.version_dict = version_dict
        self.version = (self.name, (version_dict['numeric'], version_dict['numeric2'], version_dict['numeric3']),
                        version_dict['str'], version_dict['serie'])
