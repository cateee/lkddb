#!/usr/bin/python
#: lkddb/linux/__init__.py : scanners for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import os
import os.path
import subprocess

import lkddb
import lkddb.tables

# sources
from .kbuild import kver, makefiles, kconfigs
from . import browse_sources
from parse_devicetables import *
from parse_others import *


def register_linux_browsers(tree):

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
        if task == lkddb.TASK_BUILD:
            self.retrive_version()
        lkddb.tables.register_linux_tables(self)
        if task == lkddb.TASK_BUILD:
            register_linux_browsers(self)

    def retrive_version(self):
        "Makefile, scripts/setlocalversion -> return (ver_number, ver_string, released)"
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

        version_dict['numeric'] =  ( version_dict["version"]    * 0x10000 +
                                     version_dict["patchlevel"] * 0x100   +
                                     version_dict["sublevel"]   )
        version_dict['extra'] = version_dict["EXTRAVERSION"]
        if version_dict['numeric'] == 0x02040f and version_dict['extra'] == "-greased-turkey":
            version_dict["name"] = "greased-turkey"
            version_dict['extra'] = ""
        else:
           version_dict["name"] = version_dict.get("NAME", "")
        if version_dict["VERSION"] >= "3" and version_dict["SUBLEVEL"] == "0":
            # 3.x versions
            version_dict['str'] = version_dict["VERSION"] +"."+ version_dict["PATCHLEVEL"] + version_dict['extra']
        else:
            version_dict['str'] = version_dict["VERSION"] +"."+ version_dict["PATCHLEVEL"] +"."+ version_dict["SUBLEVEL"] + version_dict['extra']

        if not version_dict['extra']:
            version_dict['numeric2'] = 0
        elif version_dict['extra'].isdigit():
            version_dict['numeric2'] = int(version_dict['extra'])
        elif version_dict['extra'].startswith("-rc") and version_dict['extra'][3:].isdigit():
            version_dict['numeric2'] = -0x100 + int(version_dict['extra'][3:])
        elif version_dict['extra'].startswith("-pre") and version_dict['extra'][4:].isdigit():
            version_dict['numeric2'] = -0x200 + int(version_dict['extra'][4:])
        elif version_dict['extra'].startswith("pre") and version_dict['extra'][3:].isdigit():
            version_dict['numeric2'] = -0x200 + int(version_dict['extra'][3:])
        else:
            assert False, "Unknow structure of EXTRAVERSION (%s) in kernel version" % version_dict["extra"]

        if os.path.exists(os.path.join(self.kerneldir, "scripts/setlocalversion")):
            f = open(os.path.join(self.kerneldir, "scripts/setlocalversion"))
            bang = f.readline()
            if bang.startswith("#!"):
                bang = bang[2:].strip()
                script = subprocess.Popen(bang + " scripts/setlocalversion .",
                    shell=True, cwd=self.kerneldir,
                    stdout=subprocess.PIPE)
                version_dict['local_ver'] = script.communicate()[0].strip().replace("-dirty", "")
                if script.returncode > 0:
                    version_dict['local_ver'] = ""
        else:
            version_dict['local_ver'] = ""
        if not version_dict['local_ver'] or version_dict['local_ver'] == '-dirty':
            version_dict['numeric3'] = 0
        elif version_dict['local_ver'][0] == '-' and version_dict['local_ver'][6] == '-' and version_dict['local_ver'][1:6].isdigit():
            version_dict['numeric3'] = int(version_dict['local_ver'][1:6])
        elif version_dict['numeric'] <= (0x020600 + 15):
            version_dict['numeric3'] = 0
        else:
            assert False, "Unknow structure of scripts/setlocalversion (%s) in kernel version" % version_dict["local_ver"]

        if version_dict['numeric3'] == 0  and  version_dict['numeric2'] == 0:
            # a x.y or x.y.z or x.y.z.w relase
            version_dict['serie'] = 1
        else:
            # not a x.y, x.y.z or x.y.z.w release
            version_dict['str'] += version_dict['local_ver']
            version_dict['serie'] = -1
        self.version_dict = version_dict
        self.version = (self.name, (version_dict['numeric'], version_dict['numeric2'], version_dict['numeric3']),
                        version_dict['str'], version_dict['serie'])

