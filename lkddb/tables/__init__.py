#: lkddb/linux/version.py : sources reader for Linux kernels
#
#  Copyright (c) 2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import lkddb
from lkddb import register_table

from . import linux_kbuild, linux_devicetables, linux_others

def register_linux_tables():
    register_table('kver', linux_kbuild.kver_table())
    register_table('kconf', linux_kbuild.kconf_table())
    register_table('module', linux_kbuild.module_table())
    
    linux_devicetables.register()
    linux_others.register()

