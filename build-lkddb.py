#!/usr/bin/python
#: build-lkddb.py : hardware database generator from linux kernel sources
#
#  Copyright (c) 2000,2001,2007-2010  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import sys
import optparse
import os
import os.path
import subprocess
import fnmatch
import glob

import lkddb
import lkddb.log
import lkddb.linux
import lkddb.tables


def make(options, kerneldir, dirs):
    tree = lkddb.linux.linux_kernel(lkddb.TASK_BUILD, kerneldir, dirs)
    options.tree = tree
    options.version = tree.get_strversion()
    if options.versioned:
        options.dbfile += "-" + options.version
    lkddb.init(options)
    try:
        lkddb.log.phase("init")
        tree.scan_sources()
        tree.finalize_sources()
    except:
        lkddb.log.exception("unknow error in main loop")
        raise
    lkddb.log.phase("write")
    if options.sql:
	sql = options.dbfile + ".db"
    else:
	sql = None
    tree.write(data = options.dbfile + ".data",
		list = options.dbfile + ".list",
		sql = sql)
#
# main
#

if __name__ == "__main__":
    
    usage = "Usage: %prog [options] kerneldir [subdirs...]"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, dbfile="lkddb", sql=False, versioned=False)
    parser.add_option("-q", "--quiet",	dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    parser.add_option("-b", "--base",	dest="dbfile",
                      action="store",	type="string",
                      help="base FILE name to read and write data", metavar="FILE")
    parser.add_option("-d", "--database",   dest="sql",
                      action="store_const", const=True,
                      help="save data in sqlite database")
    parser.add_option("-l", "--log",	dest="log_filename",
                      action="store",	type="string",
                      help="FILE to put log messages (default is stderr)", metavar="FILE")
    parser.add_option("-k", "--versioned",   dest="versioned",
                      action="store_const", const=True,
                      help="use versioned files (log and db)")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("missing mandatory argument: kernel source directory")
    kerneldir = os.path.normpath(args[0])
    if kerneldir[-1] != "/":
        kerneldir += "/"
    if len(args) > 1:
        dirs = args[1:]
    else:
        dirs = ("arch", "block", "crypto", "drivers", "firmware", "fs", "init",
                "ipc", "kernel", "lib", "mm", "net", "security",
                "sound", "usr", "virt")

    make(options, kerneldir, dirs)

