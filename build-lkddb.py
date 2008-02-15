#!/usr/bin/python
#: build-lkddb.py : hardware database generator from kernel sources
#
#  Copyright (c) 2000,2001,2007  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details


# this files is divided in following parts:
# - parse sources, find and expand detection
# - expand parameters in the output form
# - parse the kernel tree

import sys, os, os.path, re, fnmatch, optparse

import utils, srcparser, kbuildparser, devicetables


# --- --- --- --- #
# main parse function

post_remove = re.compile(
    r"(^\s*#\s*define\s+.*?$)|(\{\s+\})", re.MULTILINE)
ifdef_re = re.compile(
    r"^ifdef\s*(CONFIG_\w+)\s+.*?#endif", re.MULTILINE | re.DOTALL)

def parse_source(src, filename):
    "parse .c source file"
    dep = kbuildparser.list_dep(filename)
    srcparser.unwind_include(filename)
    for scanner in utils.scanners:
        for block in scanner.regex.findall(src):
	    block = srcparser.expand_block(block, filename)
	    for conf, sblock in ifdef_re.findall(block):
		sdep = dep.copy().add(conf)
		for line in scanner.splitter(sblock):
		    utils.parse_struct(scanner, scanner.fields, line, sdep, filename)
	    block = ifdef_re.sub(" ", block)
	    for line in scanner.splitter(block):
		utils.parse_struct(scanner, scanner.fields, line, dep, filename)

#-----------------------

def kernel_info(kerneldir):
    filename = os.path.join(kerneldir, "Makefile")
    f = open(filename)
    src = f.read(512)
    f.close()
    m = re.search(   r"VERSION\s*=\s*(\S+)\s+"+
		  r"PATCHLEVEL\s*=\s*(\S+)\s+"+
		    r"SUBLEVEL\s*=\s*(\S+)\s+"+
		r"EXTRAVERSION\s*=\s*(\S+)\s+", src, re.DOTALL)
    v,p,s,e = m.groups()
    return "_version_%s.%s.%s%s\t%s.%s.%s%s\t:: CONFIG__UNKNOW__\t:: Makefile" % (v,p,s,e, v,p,s,e)


#-----------------------

parser = optparse.OptionParser()
parser.set_defaults(verbose=1, dbfile="lkddb.list")
parser.add_option("-q", "--quiet", dest="verbose",
		    action="store_const", const=0,
                    help="don't print warning messages")
parser.add_option("-v", "--verbose", dest="verbose",
                    action="count",
                    help="print warning messages and extra messages")
parser.add_option("-o", "--output", dest="output",
		    action="store", type="string",
                    help="write warnings to FILE", metavar="FILE")
parser.add_option("-f", "--file", dest="dbfile",
                    action="store", type="string",
                    help="FILE to put the database", metavar="FILE")


(options, args) = parser.parse_args()

if options.output:
    logfile = open(options.output, "w")
else:
    logfile = sys.stdout
utils.log_init(verbose=options.verbose, logfile=logfile)

if len(args) < 1:
    parser.error("incorrect number of arguments")

kerneldir = args[0]
if kerneldir[-1] != "/":
    kerneldir += "/"
kerdir_len = len(kerneldir)

if len(args) > 1:
    dirs = args[1:]
else:
    dirs = ("arch", "block", "crypto", "drivers", "fs", "init",
                "ipc", "kernel", "lib", "mm", "net", "security",
		"sound", "virt")

print "doing the directory %s and the sub-dirs: %s" % (
	kerneldir, ", ".join(dirs) )


header = "### Linux Kernel Driver DataBase. See http://cateee.net/lkddb/"


skeleton_files = frozenset(("drivers/video/skeletonfb.c", "drivers/net/isa-skeleton.c",
        "drivers/net/pci-skeleton.c", "drivers/pci/hotplug/pcihp_skeleton.c",
        "drivers/usb/usb-skeleton.c",
   # these are #included in other files:
        "drivers/usb/host/ohci-pci.c", "drivers/usb/host/ehci-pci.c"
)
)

utils.lkddb_add(kernel_info(kerneldir))


for root_full, d_, files in os.walk(os.path.join(kerneldir, "include")):
    if root_full.endswith("/asm")  or  root_full.endswith("/asm-um"):
	continue
    dir = root_full[kerdir_len:]
    if dir.startswith("include/config")  or  dir.startswith("include/asm/"):
	continue
    if dir.startswith("include/asm-")  and  dir != "include/asm-generic":
	p = dir.split("/")
	if len(p) == 2:
	    dir_i = "include/asm"
	elif p[2].startswith("arch-"):
	    dir_i = "include/asm/arch" + "/".join(p[3:])
	else:
            dir_i = "include/asm/" + "/".join(p[2:])
    else:
	dir_i = dir
    # print "including dir ", dir, dir_i
    for source in files:
        filename = os.path.join(dir, source)
	filename_i = os.path.join(dir_i, source)
        f = open(os.path.join(kerneldir, filename))
        src = f.read()
        f.close()
	# print "include: ", filename, filename_i, dir_i
	srcparser.parse_header(src, kerneldir, dir_i, filename_i, is_c=False)

srcparser.unwind_include_all()

for subdir in dirs:
    if subdir == "arch":
        for arch in os.listdir(os.path.join(kerneldir, "arch/")):
            mk2 = os.path.join("arch/", arch)
            kbuildparser.parse_kbuild(kerneldir, mk2)
    else:
	kbuildparser.parse_kbuild(kerneldir, subdir)

    for root_full, d_, files in os.walk(os.path.join(kerneldir, subdir)):
	dir = root_full[kerdir_len:]
        for source in fnmatch.filter(files, "*.h"):
            filename = os.path.join(dir, source)
#	    print "# Doing header", filename
            f = open(os.path.join(kerneldir, filename))
            src = f.read()
            f.close()
            srcparser.parse_header(src, kerneldir, dir, filename, is_c=False)

    for root_full, d_, files in os.walk(os.path.join(kerneldir, subdir)):
        dir = root_full[kerdir_len:]
        for source in fnmatch.filter(files, "*.c"):
            filename = os.path.join(dir, source)
	    if filename in skeleton_files:
		continue
	    # print "# Doing", filename
            f = open(os.path.join(kerneldir, filename))
            src = f.read()
            f.close()
	    src = srcparser.parse_header(src, kerneldir, dir, filename, is_c=True)
            parse_source(src, filename)


for subdir in dirs:
    for root_full, d_, files in os.walk(os.path.join(kerneldir, subdir)):
        dir = root_full[kerdir_len:]
	for kconf in files:
	    if not kconf.startswith("Kconfig"):
		continue
            filename = os.path.join(dir, kconf)
	    #print "# Kconfig doing", filename
	    kbuildparser.parse_kconfig(kerneldir, filename)


utils.lkddb_print(options.dbfile, header)

