#!/usr/bin/python
#: lkddb/linux/browse_sources : sources reader for Linux kernels
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

# generic reader and container for source level scan

import os
import re
import glob
import fnmatch
import logging

import lkddb
import lkddb.parser

logger = logging.getLogger(__name__)

print("with special includes.  Check them from time to time.")

special_parsed_files = {
    'include/linux/compiler.h',
    'include/linux/mutex.h'
}

special_direct_includes = {
    'drivers/char/synclink_gt.c': {"include/linux/synclink.h"},
    'drivers/media/video/gspca/m5602/m5602_core.c': {"include/linux/usb.h"}
}


skeleton_files = frozenset((
    # skeleton and example files are not useful (and not compiled/used)
    "drivers/video/skeletonfb.c", "drivers/net/isa-skeleton.c",
    "drivers/net/pci-skeleton.c", "drivers/pci/hotplug/pcihp_skeleton.c",
    "drivers/usb/usb-skeleton.c",
    # these are #included in other files:
    "drivers/usb/host/ohci-pci.c", "drivers/usb/host/ehci-pci.c",
    # discard these files
    "include/linux/compiler.h", "include/linux/mutex.h",
))

field_init_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)$", re.DOTALL)


class LinuxKernelBrowser(lkddb.Browser):
    """generic reader, source level (c and h) files"""

    def __init__(self, kerneldir, dirs):
        super().__init__("linux_sources")
        self.kerneldir = kerneldir
        self.dirs = dirs
        # devices:
        self.scanners = []

    def register(self, scanner):
        self.scanners.append(scanner)

    def scan(self):
        lkddb.Browser.scan(self)
        orig_cwd = os.getcwd()
        # adding exceptions
        lkddb.parser.parsed_files.update(special_parsed_files)
        lkddb.parser.direct_includes.update(special_direct_includes)
        try:
            os.chdir(self.kerneldir)
            lkddb.log.phase("Headers")
            headers_to_read = []
            lkddb.parser.include_dirs.append('include')
            for root, dirs, files in os.walk("include"):
                # os.walk supports in-place substitution
                # We sort for reproducibility
                dirs.sort()
                lkddb.parser.remember_file(fnmatch.filter(files, "*.h"), root)
                p = root.split("/")
                if p[-1] in ('uapi', 'generated'):
                    lkddb.parser.include_dirs.append(root)
                if len(p) < 2 or p[1] in ("asm", "asm-um", "config"):
                    continue
                headers_to_read.append((files, root))
            for arch_incl in sorted(glob.glob("arch/*/include")):
                lkddb.parser.include_dirs.append(arch_incl)
                for root, dirs, files in os.walk(arch_incl):
                    dirs.sort()
                    lkddb.parser.remember_file(fnmatch.filter(files, "*.h"), root)
                    p = root.split("/")
                    if p[-1] in ('uapi', 'generated'):
                        lkddb.parser.include_dirs.append(root)
                    if len(p) < 3 or p[2] != "include":
                        continue
                    headers_to_read.append((files, root))

            for subdir in self.dirs:
                for root, dirs, files in os.walk(subdir):
                    dirs.sort()
                    lkddb.parser.remember_file(fnmatch.filter(files, "*.h"), root)
                    if root.endswith('include'):
                        lkddb.parser.include_dirs.append(root)
                    headers_to_read.append((fnmatch.filter(files, "*.h"), root))

            for files, path in headers_to_read:
                for source in sorted(files):
                    filename = os.path.join(path, source)
                    if filename in skeleton_files:
                        continue
                    logger.debug("Reading include " + filename)
                    lkddb.parser.parse_header(filename, return_source=False)

            lkddb.log.phase("Sources")
            for subdir in self.dirs:
                for root, dirs, files in os.walk(subdir):
                    dirs.sort()
                    for source in sorted(fnmatch.filter(files, "*.c")):
                        filename = os.path.join(root, source)
                        if filename in skeleton_files:
                            continue
                        logger.debug("Reading file " + filename)
                        src = lkddb.parser.parse_header(filename, return_source=True)
                        lkddb.parser.unwind_include(filename)
                        for s in self.scanners:
                            try:
                                s.in_scan(src, filename)
                            except RecursionError:
                                logger.error("Recursion error in file %s" % filename)
        finally:
            os.chdir(orig_cwd)

    def finalize(self):
        lkddb.Browser.finalize(self)
        for s in self.scanners:
            s.finalize()


post_remove = re.compile(
    r"(^\s*#\s*define\s+.*?$)|({\s+})", re.MULTILINE)
ifdef_re = re.compile(
    r"^ifdef\s*(CONFIG_\w+)\s+.*?#endif", re.MULTILINE | re.DOTALL)


class struct_parent_scanner(lkddb.Scanner):

    def __init__(self, browser, makefiles):
        super().__init__("struct_parent_scanner")
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
        """parse .c source file"""
        dep = self.makefiles.list_dep(filename)
        for scanner in self.scanners:
            for block in scanner.regex.findall(src):
                block = lkddb.parser.expand_block(block, filename)
                for conf, sblock in ifdef_re.findall(block):  # here
                    sdep = dep.copy().add(conf)
                    for line in scanner.splitter(sblock):
                        parse_struct(scanner, scanner.struct_fields, line, sdep, filename)
                # TODO:  optimize the second call.. only one re call
                block = ifdef_re.sub(" ", block)
                for line in scanner.splitter(block):
                    parse_struct(scanner, scanner.struct_fields, line, dep, filename)


subfield_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)(\.[A-Za-z_0-9]*\s*=\s*.*)$", re.DOTALL)


def parse_struct(scanner, fields, line, dep, filename, ret=False):
    """convert a struct (array of parameters) into a dictionary"""
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
                    raise lkddb.ParserError("in parse_line(): %s, %s, %s" % (filename, line, param))
            res[field] = value
        else:
            try:
                res[fields[nparam]] = param
            except IndexError:
                logger.exception("Index error: %s, %s, %s, %s" %
                                 (scanner.name, fields, line, filename))
                return {}
        nparam += 1
    if res:
        if ret:
            return res
        scanner.raw.append((res, filename, dep))
