#: lkddb/linux/version.py : sources reader for Linux kernels
#
#  Copyright (c) 2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

from . import linux_kbuild, linux_devicetables, linux_others

def register_linux_tables(tree):
    tree.register_table('kver', linux_kbuild.kver_table())
    tree.register_table('kconf', linux_kbuild.kconf_table())
    tree.register_table('module', linux_kbuild.module_table())
    tree.register_table('firmware', linux_kbuild.firmware_table())
    
    linux_devicetables.register(tree)
    linux_others.register(tree)

