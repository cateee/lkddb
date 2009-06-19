#!/usr/bin/python
#: build-lkddb.py : hardware database generator from linux kernel sources
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import sys
import optparse
import os
import os.path
import subprocess
import fnmatch
import glob

import lkddb
import lkddb.linux
import lkddb.tables


def make(options, logfile, kerneldir, dirs):

    lkddb.init(options.verbose, logfile)
    lkddb.tables.register_linux_tables()
    lkddb.linux.register_browsers(kerneldir, dirs)
    try:
        lkddb.phase("init")
        lkddb.scan_sources()
        lkddb.finalize_sources()
    except:
        lkddb.print_exception("unknow error in main loop")
        raise
    lkddb.phase("write")
    lkddb.write(data = options.dbfile + ".data",
		lines = options.dbfile + ".lines")

#
# main
#

if __name__ == "__main__":
    
    usage = "Usage: %prog [options] kerneldir [subdirs...]"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, dbfile="lkddb")
    parser.add_option("-q", "--quiet",	dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    parser.add_option("-b", "--base",	dest="dbfile",
                      action="store",	type="string",
                      help="base FILE name to read and write data", metavar="FILE")
    parser.add_option("-l", "--log",	dest="logfile",
                      action="store",	type="string",
                      help="FILE to put log messages (default is stderr)", metavar="FILE")
    (options, args) = parser.parse_args()

    if options.logfile:
        if options.logfile == "-":
	        logfile = sys.stdout
        else:
            logfile = open(options.logfile, "w")
    else:
	    logfile = sys.stderr

    if len(args) < 1:
        parser.error("missing mandatory argument: kernel source directory")
    kerneldir = os.path.normpath(args[0])
    if kerneldir[-1] != "/":
        kerneldir += "/"
    if len(args) > 1:
        dirs = args[1:]
    else:
        dirs = ("arch", "block", "crypto", "drivers", "fs", "init",
                "ipc", "kernel", "lib", "mm", "net", "security",
                "sound", "virt")

    make(options, logfile, kerneldir, dirs)

