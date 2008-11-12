#!/usr/bin/python
#: build-lkddb.py : hardware database generator from kernel sources
#
#  Copyright (c) 2000,2001,2007,2008  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import sys, os, subprocess, optparse, fnmatch, glob
import utils, scanners, srcparser, kbuildparser


# --------------------------


skeleton_files = frozenset(("drivers/video/skeletonfb.c", "drivers/net/isa-skeleton.c",
        "drivers/net/pci-skeleton.c", "drivers/pci/hotplug/pcihp_skeleton.c",
        "drivers/usb/usb-skeleton.c",
   # these are #included in other files:
        "drivers/usb/host/ohci-pci.c", "drivers/usb/host/ehci-pci.c"
)
)

def read_includes(files, dir, dir_i):
    # print "including dir ", dir, dir_i
    for source in files:
        filename_i = os.path.join(dir_i, source)
        f = open(os.path.join(dir, source))
        src = f.read()
        f.close()
        # print "include: ", filename, filename_i, dir_i
        srcparser.parse_header(src, filename_i, discard_source=True)


def parse_kernel(dirs):
    utils.log("PHASE: headers")
    for dir, d_, files in os.walk("include"):
	p = dir.split("/")
	if len(p) < 2 or p[1] == "asm"  or  p[1] == "asm-um"  or  p[1] == "config":
	    continue
        if p[1].startswith("asm-")  and  p[1] != "asm-generic":
            if len(p) == 2:
                dir_i = "include/asm"
            elif p[2].startswith("arch-"):
                dir_i = "include/asm/arch" + "/".join(p[3:])
            else:
                dir_i = "include/asm/" + "/".join(p[2:])
        else:
            dir_i = dir
	read_includes(files, dir, dir_i)
    for arch_incl in glob.glob("arch/*/include"):
        for dir, d_, files in os.walk(arch_incl):
            p = dir.split("/")
            if len(p) < 3  or  p[2] != "include":
                continue
	    dir_i = "include/" + "/".join(p[3:])
	    read_includes(files, dir, dir_i)

    srcparser.unwind_include_all()

    utils.log("PHASE: makefile and sources")
    for subdir in dirs:
        if subdir == "arch":
            for arch in os.listdir("arch/"):
                mk2 = os.path.join("arch/", arch)
                kbuildparser.parse_kbuild(mk2)
        else:
            kbuildparser.parse_kbuild(subdir)

        for dir, d_, files in os.walk(subdir):
            for source in fnmatch.filter(files, "*.h"):
                utils.filename = os.path.join(dir, source)
#           print "# Doing header", filename
                f = open(utils.filename)
                src = f.read()
                f.close()
                srcparser.parse_header(src, utils.filename, discard_source=True)

        for dir, d_, files in os.walk(subdir):
            for source in fnmatch.filter(files, "*.c"):
                utils.filename = os.path.join(dir, source)
                if utils.filename in skeleton_files:
                    continue
                # print "# Doing", filename
                f = open(utils.filename)
                src = f.read()
                f.close()
                src = srcparser.parse_header(src, utils.filename, discard_source=False)
                srcparser.parse_source(src, utils.filename)

    utils.log("PHASE: Kconfig")
    for subdir in dirs:
        for dir, d_, files in os.walk(subdir):
            for kconf in fnmatch.filter(files, "Kconfig*"):
                utils.filename = os.path.join(dir, kconf)
                #print "# Kconfig doing", filename
                kbuildparser.parse_kconfig(utils.filename)

    utils.log("PHASE: formatter")
    utils.lkddb_build()
    utils.log("PHASE: end")


def get_kernel_version(kerneldir):
    dict = {}
    f = open("Makefile")
    for record in ("VERSION", "PATCHLEVEL", "SUBLEVEL", "EXTRAVERSION"):
        line = f.readline().replace(" ","").strip()
        assert line.startswith(record+"=")
        dict[record] = line.replace(record+"=", "")
    version =  (  int(dict["VERSION"])    * 0x10000 +
		  int(dict["PATCHLEVEL"]) * 0x100   +
		  int(dict["SUBLEVEL"])   )
    extra = dict["EXTRAVERSION"]
    ver_str = dict["VERSION"] +"."+ dict["PATCHLEVEL"] +"."+ dict["SUBLEVEL"] + extra

    c = utils.conn.cursor()
    row = c.execute('SELECT min_ver, max_ver, head_tag FROM version WHERE type = 1;').fetchone()
    if not row:
	row = (0xffffff, 0x000000, "(none)")
    min_ver, max_ver, head_tag = row
    localver = subprocess.Popen("/bin/sh scripts/setlocalversion", shell=True, cwd=kerneldir,
		stdout=subprocess.PIPE).communicate()[0].strip().replace("-dirty", "")
    if localver  or  extra.startswith('-'):
	# not a x.y.z or x.y.z.w release
	if version < max_ver:
	    utils.die(1, "error: old non-stable version found (in db: %x, actual: %x, tag:'%s')" %
		(max_ver, version, extra+localver))
	if ver_str+localver != head_tag:
	    c.execute('INSERT OR REPLACE INTO version (type, max_ver, head_tag) VALUES (1,-1,?);',
			(ver_str+localver,))
	    utils.conn.commit()
	utils.version_str = ver_str+localver
	return -1
    else:
	if version > max_ver:
            c.execute('INSERT OR REPLACE INTO version (type, min_ver, max_ver, head_tag) VALUES (1,?,?,?);',
                (min(version, min_ver), max(version,max_ver), ver_str) )
	    utils.conn.commit()
	elif version < min_ver:
	    c.execute('INSERT OR REPLACE INTO version (type, min_ver) VALUES (1,?);',
		(min(version,min_ver),) )
	    utils.conn.commit()
	utils.version_str = ver_str
	return version


# -------------------------------------------------------------------

def main():
    usage = "Usage: %prog [options] kerneldir [subdirs...]"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, dbfile="lkddb.db")
    parser.add_option("-q", "--quiet", 	dest="verbose",
                    action="store_const", const=0,
                    help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                    action="count",
                    help="increments verbosity")
    parser.add_option("-o", "--output", dest="output",
                    action="store", 	type="string",
                    help="FILE to put messages (default is to stdout)", metavar="FILE")
    parser.add_option("-f", "--dbfile", dest="dbfile",
                    action="store", 	type="string",
                    help="path to sqlite database", metavar="FILE")
    parser.add_option("-l", "--list",   dest="lkddb_list",
                    action="store", 	type="string",
                    help="additionally create a text .list file", metavar="FILE")

    (options, args) = parser.parse_args()

    if options.output  and  options.output != "-":
        logfile = open(options.output, "w")
    else:
        logfile = sys.stdout

    if len(args) < 1:
        parser.error("incorrect number of arguments: I need the path to kernel source")
    kerneldir = os.path.normpath(args[0])
    if kerneldir[-1] != "/":
        kerneldir += "/"
    if len(args) > 1:
        dirs = args[1:]
    else:
        dirs = ("arch", "block", "crypto", "drivers", "fs", "init",
                "ipc", "kernel", "lib", "mm", "net", "security",
                "sound", "virt")

    utils.init(options, logfile, kerneldir)
    utils.program_cwd = os.getcwd()
    os.chdir(kerneldir)

    try:
        scanners.scanner_init()
        kbuildparser.kconfig_init()
        utils.version_number = get_kernel_version(kerneldir)
        parse_kernel(dirs)
    except:
	print "EXCEPTION in", utils.filename
	raise


if __name__ == "__main__":
    main()

