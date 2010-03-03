#!/usr/bin/python
#: consolidate.py : consolidate data from different version
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
import lkddb.linux
import lkddb.tables


def make(options, logfile, args):

    lkddb.init(options.verbose, logfile)
    tree = lkddb.linux.linux_kernel(None, (,)
    lkddb.tables.register_linux_tables(tree))
    consolidate = read_data(options.consolidate, False)
    for dbfile in args:
	consolidate_data(dbfile, False)

    try:
        lkddb.phase("init")
        lkddb.scan_sources()
        lkddb.finalize_sources()
    except:
        lkddb.print_exception("unknow error in main loop")
        raise
    lkddb.phase("write")
    if options.sql:
	sql = options.dbfile + ".db"
    else:
	sql = None
    lkddb.write(data = options.dbfile + ".data",
		list = options.dbfile + ".list",
		sql = sql)

#
# main
#

if __name__ == "__main__":
    
    usage = "Usage: %prog [options] file-to-consolidate..."
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, consolidate="clkddb")
    parser.add_option("-q", "--quiet",	dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    parser.add_option("-c", "--consolidate", dest="consolidate",
                      action="store",	type="string",
                      help="base FILE name to read and write data", metavar="FILE")
    parser.add_option("-l", "--log",	dest="logfile",
                      action="store",	type="string",
                      help="FILE to put log messages (default is stderr)", metavar="FILE")
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("missing mandatory argument: file to consolidate")

    if options.logfile:
        if options.logfile == "-":
                logfile = sys.stdout
        else:
            logfile = open(options.logfile, "w")
    else:
            logfile = sys.stderr

    make(options, logfile, args)

