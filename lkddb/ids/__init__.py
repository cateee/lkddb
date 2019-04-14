#!/usr/bin/python
#: lkddb/ids/__init__.py : scanners for ids files
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import time
import logging

import lkddb

logger = logging.getLogger(__name__)

tables = {}


class IdsTree(lkddb.Tree):

    def __init__(self, task, pci_ids, usb_ids, eisa_ids, zorro_ids):
        super().__init__("ids_files", tables)
        self.pci_ids_filename = pci_ids
        self.usb_ids_filename = usb_ids
        self.eisa_ids_filename = eisa_ids
        self.zorro_ids_filename = zorro_ids
        import lkddb.tables.ids_tables
        if task == lkddb.TASK_BUILD:
            self.browser = IdsBrowser(self)
            self.register_browser(self.browser)

    def retrieve_version(self):
        self.version = ("ids_files", (int(time.time()/60/60),), "", -1)


class IdsBrowser(lkddb.Browser):

    def __init__(self, tree):
        super().__init__("ids_file_browser")

        self.tree = tree
        self.scanners = []
        self.pci_ids_filename = tree.pci_ids_filename
        self.usb_ids_filename = tree.usb_ids_filename
        self.eisa_ids_filename = tree.eisa_ids_filename
        self.zorro_ids_filename = tree.zorro_ids_filename
        self.pci_ids_table = tree.get_table('pci_ids')
        self.pci_class_ids_table = tree.get_table('pci_class_ids')
        self.usb_ids_table = tree.get_table('usb_ids')
        self.usb_class_ids_table = tree.get_table('usb_class_ids')
        self.eisa_ids_table = tree.get_table('eisa_ids')
        self.zorro_ids_table = tree.get_table('zorro_ids')

    def register(self, scanner):
        self.scanners.append(scanner)

    def scan(self):
        lkddb.Browser.scan(self)

        # pci.ids
        logger.info("=== pci.ids")
        f = open(self.pci_ids_filename, 'r', encoding='utf8', errors='replace')
        part = "H"		# H : header
        v0, v1, v2 = -1, -1, -1
        for line in f:
            if part == "H":
                if line[0] == "#":
                    # find Version: and Date:
                    continue
                part = "D"
            line = line.rstrip()
            if line == "" or line[0] == "#":
                continue
            line = line.expandtabs().replace("        ", "\t")
            s = line.split()
            if line[0] == "C":
                part = "C"
            if part == "D":
                if line[0] != "\t":
                    v0 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.pci_ids_table.add_row((v0, -1, -1, -1, name))
                elif line[1] != "\t":
                    v1 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.pci_ids_table.add_row((v0, v1, -1, -1, name))
                else:
                    a1 = int(s[0], 0x10)
                    a2 = int(s[1], 0x10)
                    name = " ".join(s[2:])
                    self.pci_ids_table.add_row((v0, v1, a1, a2, name))
            elif part == "C":
                if line[0] != "\t":
                    v0 = int(s[1], 0x10)
                    name = " ".join(s[2:])
                    self.pci_class_ids_table.add_row((v0, -1, -1, name))
                elif line[1] != "\t":
                    v1 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.pci_class_ids_table.add_row((v0, v1, -1, name))
                else:
                    v2 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.pci_class_ids_table.add_row((v0, v1, v2, name))
            else:
                assert False, "Parser error in pci.ids, with 'part=%s'" % part
        f.close()

        # usb.ids
        logger.info("=== usb.ids")
        f = open(self.usb_ids_filename, 'r', encoding='utf8', errors='replace')
        part = "H"
        v0, v1, v2 = -1, -1, -1
        for line in f:
            if part == "H":
                if line[0] == "#":
                    continue
                part = "D"
            if part == "E":
                # we don't read last part of usb.ids
                continue
            line = line.rstrip()
            if line == "" or line[0] == "#":
                continue
            line = line.expandtabs().replace("        ", "\t")
            s = line.split()
            if line[0] == "C":
                part = "C"
            if part == "C" and line[0] != "C" and line[0].isalpha():
                part = "E"
                continue
            if part == "D":
                if line[0] != "\t":
                    v0 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.usb_ids_table.add_row((v0, -1, name))
                elif line[1] != "\t":
                    v1 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.usb_ids_table.add_row((v0, v1, name))
                else:
                    raise lkddb.DataError("Importing usb interface fields on usb.id is not yet implemented")
            elif part == "C":
                if line[0] != "\t":
                    v0 = int(s[1], 0x10)
                    name = " ".join(s[2:])
                    self.usb_class_ids_table.add_row((v0, -1, -1, name))
                elif line[1] != "\t":
                    v1 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.usb_class_ids_table.add_row((v0, v1, -1, name))
                else:
                    v2 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.usb_class_ids_table.add_row((v0, v1, v2, name))
            else:  # part "E"
                pass

        # eisa.ids
        logger.info("=== eisa.ids'")
        f = open(self.eisa_ids_filename, 'r', encoding='utf8', errors='replace')
        part = "H"
        for line in f:
            if part == "H":
                if line[0] == "#":
                    continue
                part = "D"
            line = line.strip()
            if line == "" or line[0] == "#":
                continue
            id_str = line[:7]
            assert line[7] == " " or line[7] == "\t", "char '%s', line: %s" % (line[7], line)
            name = line[9:-1]
            self.eisa_ids_table.add_row((id_str, name))

        # zorro.ids
        logger.info("=== zorro.ids'")
        f = open(self.zorro_ids_filename, 'r', encoding='utf8', errors='replace')
        part = "H"
        v0, v1 = -1, -1
        for line in f:
            if part == "H":
                if line[0] == "#":
                    continue
                part = "D"
            line = line.rstrip()
            if line == "" or line[0] == "#":
                continue
            line = line.expandtabs().replace("        ", "\t")
            s = line.split()
            if part == "D":
                if line[0] != "\t":
                    v0 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.zorro_ids_table.add_row((v0, -1, name))
                elif line[1] != "\t":
                    v1 = int(s[0], 0x10)
                    name = " ".join(s[1:])
                    self.zorro_ids_table.add_row((v0, v1, name))
                else:
                    assert False, "Error in zorro.ids, with line: %s" % line

    def finalize(self):
        lkddb.Browser.finalize(self)
