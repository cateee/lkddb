#!/usr/bin/python
#: ids_importer.py : import ids
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import sys
import optparse

import lkddb
import lkddb.ids


def make(options, paths):
    tree = lkddb.ids.ids_files(lkddb.TASK_BUILD, paths)
    options.tree = tree
    options.version = tree.get_strversion()
    if options.versioned:
        options.dbfile += "-" + options.version
    lkddb.init(options)
    try:
        lkddb.log.phase("scan")
        tree.scan_sources()
        lkddb.log.phase("finalize")
        tree.finalize_sources()
    except:
        lkddb.log.exception("unknow error in main loop")
        raise
    lkddb.log.phase("write")
    if options.sql:
        sql = options.dbfile + ".db"
    else:
        sql = None
    tree.write(data_filename = options.dbfile + ".data",
                list_filename = options.dbfile + ".list",
                sql_filename = sql)

#
# main
#

if __name__ == "__main__":

    usage = "Usage: %prog [options] pci.ids usb.ids eisa.ids zorro.ids"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, dbfile="ids", sql=False, versioned=False)
    parser.add_option("-q", "--quiet",  dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    parser.add_option("-b", "--base",   dest="dbfile",
                      action="store",   type="string",
                      help="base FILE name to read and write data", metavar="FILE")
    parser.add_option("-d", "--database",   dest="sql",
                      action="store_const", const=True,
                      help="save data in sqlite database")
    parser.add_option("-l", "--log",    dest="log_filename",
                      action="store",   type="string",
                      help="FILE to put log messages (default to stderr)", metavar="FILE")
    parser.add_option("-k", "--versioned",   dest="versioned",
                      action="store_const", const=True,
                      help="ignored (for compatibility)")
    (options, args) = parser.parse_args()

    if len(args) != 4:
        parser.error("needed exactly 4 files: pci.ids usb.ids eisa.ids zorro.ids")

    options.versioned = False
    make(options, args)


