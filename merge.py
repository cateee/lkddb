#!/usr/bin/python
#: merge.py : merge data from different version into a big database
#
#  Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import optparse

import lkddb
import lkddb.linux
import lkddb.ids


def make(options, args):

    lkddb.init(options)

    linux_tree = lkddb.linux.LinuxKernelTree(lkddb.TASK_CONSOLIDATE, None, [])
    ids_tree = lkddb.ids.IdsTree(lkddb.TASK_CONSOLIDATE, None)
    storage = lkddb.Storage((linux_tree, ids_tree))

    lkddb.logger.info("=== Read files to consolidate")

    for f in args:
        storage.read_data(f)

        lkddb.logger.info("=== Write consolidate main file")
    storage.write_data(filename=options.consolidated)


#
# main
#

if __name__ == "__main__":

    usage = "Usage: %prog [options] file-to-consolidate..."
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, consolidated="lkddb-all.data", timed_logs=False)
    parser.add_option("-q", "--quiet",	dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    parser.add_option("-o", "--output", dest="consolidated",
                      action="store",	type="string",
                      help="base FILE name to read and write data", metavar="FILE")
    parser.add_option("-l", "--log",	dest="log_filename",
                      action="store",	type="string",
                      help="FILE to put log messages (default is stderr)", metavar="FILE")
    options_, args_ = parser.parse_args()

    if len(args_) < 1:
        parser.error("missing mandatory argument: on or more files to consolidate")

    options_.versioned = False
    make(options_, args_)
