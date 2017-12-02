#!/usr/bin/python
#: build-lkddb.py : hardware database generator from linux kernel sources
#
#  Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import optparse
import os.path

import lkddb
import lkddb.log
import lkddb.linux


def make(options, kerneldir, dirs):
    tree = lkddb.linux.LinuxKernelTree(lkddb.TASK_BUILD, kerneldir, dirs)
    options.version = tree.get_strversion()
    if options.versioned:
        options.dbfile += "-" + options.version
    lkddb.init(options)
    lkddb.logger.info("=== Scan Linux kernel sources")
    tree.scan_sources()
    lkddb.logger.info("=== Preparing data")
    tree.finalize_sources()
    lkddb.logger.info("=== Write data")
    if options.sql:
        sql = options.dbfile + ".db"
    else:
        sql = None
    tree.write(data_filename=options.dbfile + ".data",
               list_filename=options.dbfile + ".list",
               sql_filename=sql)


#
# main
#

if __name__ == "__main__":

    usage = "Usage: %prog [options] kerneldir [subdirs...]"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, dbfile="lkddb", sql=False, versioned=False, timed_logs=False)
    parser.add_option("-q", "--quiet", dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increase verbosity")
    parser.add_option("-b", "--base", dest="dbfile",
                      action="store", type="string",
                      help="base FILE name to read and write data", metavar="FILE")
    parser.add_option("-d", "--database", dest="sql",
                      action="store_const", const=True,
                      help="save data in sqlite database")
    parser.add_option("-l", "--log", dest="log_filename",
                      action="store", type="string",
                      help="FILE to put log messages (default to stderr)", metavar="FILE")
    parser.add_option("-k", "--versioned", dest="versioned",
                      action="store_const", const=True,
                      help="append version to file names (log and data)")
    options_, args_ = parser.parse_args()

    if len(args_) < 1:
        parser.error("missing mandatory argument: kernel source directory")
    kerneldir_ = os.path.normpath(args_[0])
    if kerneldir_[-1] != "/":
        kerneldir_ += "/"
    if len(args_) > 1:
        dirs_ = args_[1:]
    else:
        dirs_ = ("arch", "block", "crypto", "drivers", "firmware", "fs", "init",
                 "ipc", "kernel", "lib", "mm", "net", "security",
                 "sound", "usr", "virt")

    make(options_, kerneldir_, dirs_)
