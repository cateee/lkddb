#: lkddb/linux/version.py : sources reader for Linux kernels
#
#  Copyright (c) 2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details


def register_linux_tables(tree):
    from . import linux_kbuild, linux_devicetables, linux_others

    tree.register_table('kver', linux_kbuild.kver_table())
    tree.register_table('kconf', linux_kbuild.kconf_table())
    tree.register_table('module', linux_kbuild.module_table())
    tree.register_table('firmware', linux_kbuild.firmware_table())
    
    linux_devicetables.register(tree)
    linux_others.register(tree)


def register_ids_tables(tree):
    from . import ids_tables

    tree.register_table('pci_ids', ids_tables.pci_ids_table())
    tree.register_table('pci_class_ids', ids_tables.pci_class_ids_table())
    tree.register_table('usb_ids', ids_tables.usb_ids_table())
    tree.register_table('usb_class_ids', ids_tables.usb_class_ids_table())
    tree.register_table('eisa_ids', ids_tables.eisa_ids_table())
    tree.register_table('zorro_ids', ids_tables.zorro_ids_table())

