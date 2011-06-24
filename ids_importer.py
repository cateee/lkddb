#!/usr/bin/python
#: ids_importer.py : import ids
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details


import sys

import lkddb


dbfile="lkddb.db"


conn = None
def db_init():
    global conn
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS pci_ids (" +
	"vendor     INTEGER, " +
	"device     INTEGER, " +
	"subvendor  INTEGER, " +
	"name       TEXT, " +
	"UNIQUE(vendor, device, subvendor));")
    c.execute("CREATE TABLE IF NOT EXISTS pci_class_ids (" +
        "class      INTEGER, " +
        "subclass   INTEGER, " +
        "prog_if    INTEGER, " +
        "name       TEXT, " +
        "UNIQUE(class, subclass, prog_if));")
    c.execute("CREATE TABLE IF NOT EXISTS usb_ids (" +
        "vendor     INTEGER, " +
        "device     INTEGER, " +
        "interface  INTEGER, " +
        "name       TEXT, " +
        "UNIQUE(vendor, device, interface));")
    c.execute("CREATE TABLE IF NOT EXISTS usb_class_ids (" +
        "class      INTEGER, " +
        "subclass   INTEGER, " +
        "protocol   INTEGER, " +
        "name       TEXT, " +
        "UNIQUE(class, subclass, protocol));")
    c.execute("CREATE TABLE IF NOT EXISTS eisa_ids (" +
        "id         TEXT UNIQUE, " +
        "name       TEXT); ")
    c.execute("CREATE TABLE IF NOT EXISTS zorro_ids (" +
        "manufacturer INTEGER, " +
        "product      INTEGER, " +
        "name         TEXT, " +
        "UNIQUE(manufacturer, product));")
    conn.commit()

def pci_ids(filename, outfilename):
    insert_pci = "INSERT OR IGNORE INTO pci_ids (vendor, device, subvendor, name) VALUES (?,?,?,?);"
    insert_pci_class = "INSERT OR IGNORE INTO pci_class_ids (class, subclass, prog_if, name) VALUES (?,?,?,?);"
    out = open(outfilename, "w")
    c = conn.cursor()
    part = "H"
    v0, v1, v2 = -1, -1, -1
    for line in open(filename):
        if part == "H":
            if line[0] == "#":
                out.write(line)
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
	        c.execute(insert_pci, (v0, -1, -1, name))
		out.write("pci_ids\t%04x\t'%s'\n" % (v0, name))
	    elif line[1] != "\t":
	        v1 = int(s[0], 0x10)
		name = " ".join(s[1:])
                c.execute(insert_pci, (v0, v1, -1, name))
		out.write("pci_ids\t%04x %04x\t'%s'\n" % (v0, v1, name))
	    else:
		a1 = int(s[0], 0x10)
		a2 = int(s[1], 0x10)
	        v2 = a1 * 0x10000 + a2
		name = " ".join(s[2:])
                c.execute(insert_pci, (v0, v1, v2, name))
		out.write("pci_ids\t%04x %04x %04x %04x\t'%s'\n" % (v0, v1, a1, a2, name))
	else:
            if line[0] != "\t":
                v0 = int(s[1], 0x10)
		name = " ".join(s[2:])
                c.execute(insert_pci_class, (v0, -1, -1, name))
		out.write("pci_ids\tC %02x\t'%s'\n" % (v0, v1))
            elif line[1] != "\t":
                v1 = int(s[0], 0x10)
		name = " ".join(s[1:])
                c.execute(insert_pci_class, (v0, v1, -1, name))
		out.write("pci_ids\tC %02x %02x\t'%s'\n" % (v0, v1, name))
            else:
                v2 = int(s[0], 0x10)
		name = " ".join(s[1:])
                c.execute(insert_pci_class, (v0, v1, v2, name))
		out.write("pci_ids\tC %02x %02x %02x\t'%s'\n" % (v0, v1, v2, name))
    conn.commit()
    out.close()


def usb_ids(filename, outfilename):
    insert_usb = "INSERT OR IGNORE INTO usb_ids (vendor, device, interface, name) VALUES (?,?,?,?);"
    insert_usb_class = "INSERT OR IGNORE INTO usb_class_ids (class, subclass, protocol, name) VALUES (?,?,?,?);"
    out = open(outfilename, "w")
    c = conn.cursor()
    part = "H"
    v0, v1, v2 = -1, -1, -1
    for line in open(filename):
        if part == "H":
            if line[0] == "#":
                out.write(line)
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
                c.execute(insert_usb, (v0, -1, -1, name))
                out.write("usb_ids\t%04x\t'%s'\n" % (v0, name))
            elif line[1] != "\t":
                v1 = int(s[0], 0x10)
                name = " ".join(s[1:])
                c.execute(insert_usb, (v0, v1, -1, name))
                out.write("usb_ids\t%04x %04x\t'%s'\n" % (v0, v1, name))
            else:
                v2 = int(s[0], 0x10)
                name = " ".join(s[1:])
                c.execute(insert_usb, (v0, v1, v2, name))
                out.write("usb_ids\t%04x %04x %04x %04x\t'%s'\n" % (v0, v1, v2, name))
		print line
		assert False
        else:
            if line[0] != "\t":
                v0 = int(s[1], 0x10)
                name = " ".join(s[2:])
                c.execute(insert_usb_class, (v0, -1, -1, name))
                out.write("usb_ids\tC %02x\t'%s'\n" % (v0, v1))
            elif line[1] != "\t":
                v1 = int(s[0], 0x10)
                name = " ".join(s[1:])
                c.execute(insert_usb_class, (v0, v1, -1, name))
                out.write("usb_ids\tC %02x %02x\t'%s'\n" % (v0, v1, name))
            else:
                v2 = int(s[0], 0x10)
                name = " ".join(s[1:])
                c.execute(insert_usb_class, (v0, v1, v2, name))
                out.write("usb_ids\tC %02x %02x %02x\t'%s'\n" % (v0, v1, v2, name))
    conn.commit()
    out.close()

def eisa_ids(filename, outfilename):
    insert_eisa = "INSERT OR IGNORE INTO eisa_ids (id, name) VALUES (?,?);"
    out = open(outfilename, "w")
    c = conn.cursor()
    part = "H"
    for line in open(filename):
        if part == "H":
            if line[0] == "#":
                out.write(line)
                continue
            part = "D"
        line = line.strip()
        if line == ""  or  line[0] == "#":
            continue
	id   = line[:7]
	name = line[9:-1]
	c.execute(insert_eisa, (id, name))
	out.write("eisa_ids\t%s\t'%s'\n" % (id, name))
    conn.commit()
    out.close()


def zorro_ids(filename, outfilename):
    insert_zorro = "INSERT OR IGNORE INTO zorro_ids (manufacturer, product, name) VALUES (?,?,?);"
    out = open(outfilename, "w")
    c = conn.cursor()
    part = "H"
    v0, v1 = -1, -1
    for line in open(filename):
        if part == "H":
            if line[0] == "#":
                out.write(line)
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
                c.execute(insert_zorro, (v0, -1, name))
                out.write("zorro_ids\t%04x\t'%s'\n" % (v0, name))
            elif line[1] != "\t":
                v1 = int(s[0], 0x10)
                name = " ".join(s[1:])
                c.execute(insert_zorro, (v0, v1, name))
                out.write("zorro_ids\t%04x %04x\t'%s'\n" % (v0, v1, name))
            else:
		print "Error in:", line
		assert False
    conn.commit()
    out.close()


def main():
    db_init()
    if len(sys.argv) > 1:
	subsys = sys.argv[1]
    else:
	subsys = None
    if not subsys  or  subsys == "pci":
        pci_ids("pci.ids", "pci.list")
    if not subsys  or  subsys == "usb":
        usb_ids("usb.ids", "usb.list")
    if not subsys  or  subsys == "eisa":
        eisa_ids("eisa.ids", "eisa.list")
    if not subsys  or  subsys == "zorro":
        zorro_ids("zorro.ids", "zorro.list")


if __name__ == "__main__":
    main()

