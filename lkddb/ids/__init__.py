#!/usr/bin/python
#: lkddb/ids/__init__.py : scanners for ids files
#
#  Copyright (c) 2000,2001,2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import os
import time

import lkddb
import lkddb.tables


class ids_files(lkddb.tree):

    def __init__(self, task, paths):
        lkddb.tree.__init__(self, "ids_files")
        self.paths = paths
        lkddb.tables.register_ids_tables(self)
        if task == lkddb.TASK_BUILD:
	    assert len(paths) >= 4, "needs 4 ids files: pci, usb, pnp, zorro"
	    self.browser = ids_file_browser(self)
	    self.register_browser(self.browser)

    def retrive_version(self):
	self.version = ("ids_files", (int(time.time()/60/60),), "", -1)


class ids_file_browser(lkddb.browser):

    def __init__(self, tree):
        lkddb.browser.__init__(self, "ids_file_browser")
	self.tree = tree
	self.pci_ids_filename = tree.paths[0]
	self.usb_ids_filename = tree.paths[1]
        self.eisa_ids_filename = tree.paths[2]
	self.zorro_ids_filename = tree.paths[3]
	self.pci_ids_table = tree.get_table('pci_ids')
	self.pci_class_ids_table = tree.get_table('pci_class_ids')
	self.usb_ids_table = tree.get_table('usb_ids')
	self.usb_class_ids_table = tree.get_table('usb_class_ids')
	self.eisa_ids_table = tree.get_table('eisa_ids')
	self.zorro_ids_table = tree.get_table('zorro_ids')

    def register(self, scanner):
        self.scanners.append(scanner)

    def scan(self):
        lkddb.browser.scan(self)

	# pci.ids
	lkddb.log.phase("pci.ids'")
	f = open(self.pci_ids_filename, 'r')
	part = "H"		# H : header
	v0, v1, v2 = -1, -1, -1
	for line in f:
	    if part == "H":
		if line[0] == "#":
           	    # find Version: and Date:
                    continue
                part = "D"
            line = line.rstrip()
            if line == ""  or  line[0] == "#":
                continue
            line = line.expandtabs().replace("        ","\t")
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
                     v2 = a1 * 0x10000 + a2
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
        lkddb.log.phase("usb.ids'")
        f = open(self.usb_ids_filename, 'r')
        part = "H"
        v0, v1, v2 = -1, -1, -1
        for line in f:
            if part == "H":
                if line[0] == "#":
                    #out.write(line)
                    continue
                part = "D"
	    if part == "E":
		# we don't read last part of usb.ids
		continue
            line = line.rstrip()
            if line == ""  or  line[0] == "#":
                continue
            line = line.expandtabs().replace("        ","\t")
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
                    lkddb.log.log("importing usb interface fields on usb.id is not yet implemented")
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
	    else: # part "E"
		pass

        # eisa.ids
        lkddb.log.phase("eisa.ids'")
        f = open(self.eisa_ids_filename, 'r')
        part = "H"
        for line in f:
            if part == "H":
                if line[0] == "#":
                    #out.write(line)
                    continue
                part = "D"
            line = line.strip()
            if line == ""  or  line[0] == "#":
                continue
            id = line[:7]
	    assert line[7] == " " or line[7] == "\t", "char '%s', line: %s" % (line[7], line) 
            name = line[9:-1]
	    self.eisa_ids_table.add_row((id, name))

        # zorro.ids
        lkddb.log.phase("zorro.ids'")
        f = open(self.zorro_ids_filename, 'r')
        part = "H"
        v0, v1 = -1, -1
        for line in f:
            if part == "H":
                if line[0] == "#":
                    #out.write(line)
                    continue
                part = "D"
            line = line.rstrip()
            if line == ""  or  line[0] == "#":
                continue
            line = line.expandtabs().replace("        ","\t")
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
        lkddb.browser.finalize(self)


