#!/usr/bin/python
#: lkddb/linux/browse_sources : sources reader for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

# generic reader and container for source level scan

import os
import re
import glob
import fnmatch

import lkddb
import lkddb.log
import lkddb.parser
from lkddb.parser import unwind_include



skeleton_files = frozenset(("drivers/video/skeletonfb.c", "drivers/net/isa-skeleton.c",
        "drivers/net/pci-skeleton.c", "drivers/pci/hotplug/pcihp_skeleton.c",
        "drivers/usb/usb-skeleton.c",
   # these are #included in other files:
        "drivers/usb/host/ohci-pci.c", "drivers/usb/host/ehci-pci.c",
   # discard these files
        "include/linux/compiler.h", "include/linux/mutex.h", "drivers/mmc/host/omap_hsmmc.c"
))


field_init_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)$", re.DOTALL)

class linux_sources(lkddb.browser):
    "generic reader, source level (c and h) files"

    def __init__(self, kerneldir, dirs):
        lkddb.browser.__init__(self, "linux_sources")
        self.kerneldir = kerneldir
        self.dirs = dirs
	# devices:
	self.scanners = []

    def register(self, scanner):
	self.scanners.append(scanner)

    def scan(self):
	lkddb.browser.scan(self)
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.kerneldir)
            lkddb.log.phase("headers")
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
  	        self.__read_includes(files, dir, dir_i)
            for arch_incl in glob.glob("arch/*/include"):
                for dir, d_, files in os.walk(arch_incl):
                    p = dir.split("/")
		    if len(p) < 3  or  p[2] != "include":
				  continue
	            dir_i = "include/" + "/".join(p[3:])
	            self.__read_includes(files, dir, dir_i)

            lkddb.parser.unwind_include_all()

            lkddb.log.phase("sources")
            for subdir in self.dirs:
                for dir, d_, files in os.walk(subdir):
	            self.__read_includes(fnmatch.filter(files, "*.h"), dir, dir)

                for dir, d_, files in os.walk(subdir):
                    for source in fnmatch.filter(files, "*.c"):
                        filename = os.path.join(dir, source)
                        if filename in skeleton_files:
                            continue
                        lkddb.log.log_extra("reading file " + filename)
                        f = open(filename)
                        src = f.read()
                        f.close()
                        src = lkddb.parser.parse_header(src, filename, discard_source=False)
			for s in self.scanners:
			    s.in_scan(src, filename)
        finally:
            os.chdir(orig_cwd)

    def finalize(self):
	lkddb.browser.finalize(self)
	for s in self.scanners:
	    s.finalize()

    def __read_includes(self, files, dir, dir_i):
        for source in files:
            filename_i = os.path.join(dir_i, source)
            if filename_i in skeleton_files:
                continue
            lkddb.log.log_extra("reading include " + filename_i)
            f = open(os.path.join(dir, source))
            src = f.read()
            f.close()
            lkddb.parser.parse_header(src, filename_i, discard_source=True)


post_remove = re.compile(
    r"(^\s*#\s*define\s+.*?$)|(\{\s+\})", re.MULTILINE)
ifdef_re = re.compile(
    r"^ifdef\s*(CONFIG_\w+)\s+.*?#endif", re.MULTILINE | re.DOTALL)


class struct_parent_scanner(lkddb.scanner):

    def __init__(self, browser, makefiles):
	lkddb.scanner.__init__(self, "struct_parent_scanner")
	self.browser = browser
	self.makefiles = makefiles
        self.scanners = []
	browser.register(self)

    def register(self, scanner):
	self.scanners.append(scanner)
	
    def finalize(self):
        for s in self.scanners:
            s.finalize()

    def in_scan(self, src, filename):
        "parse .c source file"
        dep = self.makefiles.list_dep(filename)
        unwind_include(filename)
        for scanner in self.scanners:
            for block in scanner.regex.findall(src):
                block = lkddb.parser.expand_block(block, filename)
                for conf, sblock in ifdef_re.findall(block): ### here
                    sdep = dep.copy().add(conf)
                    for line in scanner.splitter(sblock):
                        parse_struct(scanner, scanner.struct_fields, line, sdep, filename)
                # TODO:  optimize the second call.. only one re call
                block = ifdef_re.sub(" ", block)
                for line in scanner.splitter(block):
                    parse_struct(scanner, scanner.struct_fields, line, dep, filename)

subfield_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)(\.[A-Za-z_0-9]*\s*=\s*.*)$", re.DOTALL)


def parse_struct(scanner, fields, line, dep, filename, ret=False):
    "convert a struct (array of parameters) into a dictionary"
    res = {}
    nparam = 0
    for param in line:
        param = param.replace("\n", " ").strip()
        if not param:
            continue
        elif param[0] == ".":
            m = field_init_re.match(param)
            if m:
                field, value = m.groups()
            else:
                m = subfield_re.match(param)
                if m:
                    field, value = m.groups()
                    value = "{" + value + "}"
                else:
                    lkddb.die("parse_line(): %s, %s, %s" % filename, line, param)
            res[field] = value
        else:
            try:
                res[fields[nparam]] = param
            except IndexError:
                lkddb.log.exception("Error: index error: %s, %s, %s, %s" %
					(scanner.name, fields, line, filename))
                assert False, "Error: index error: %s, %s, %s, %s" % (scanner.name, fields, line, filename)
        nparam += 1
    if res:
        if ret:
            return res
        scanner.raw.append((res, filename, dep))

