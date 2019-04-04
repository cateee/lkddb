#!/usr/bin/python
#: ids_importer.py : import ids
#
#  Copyright (c) 2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import optparse
import os.path

import lkddb
import lkddb.ids


def make(options, paths):
    tree = lkddb.ids.IdsTree(lkddb.TASK_BUILD, paths)
    options.version = tree.get_strversion()
    if options.versioned:
        options.dbfile += "-" + options.version
    lkddb.init(options)
    lkddb.log.phase("=== Read 'ids' files")
    tree.scan_sources()
    lkddb.log.phase("=== Preparing data")
    tree.finalize_sources()
    lkddb.log.phase("=== Write data")
    if options.sql:
        sql = options.dbfile + ".db"
    else:
        sql = None
    tree.write(data_filename=options.dbfile + ".data",
               list_filename=options.dbfile + ".list",
               sql_filename=sql)
    dest_dir = os.path.dirname(options.dbfile)
    build_single_ids(options.dbfile + ".list", dest_dir)


def build_single_ids(filename, dest_dir):
    f = open(filename)
    lists = {'eisa_ids': [], 'pci_class_ids': [], 'pci_ids': [],
             'usb_class_ids': [], 'usb_ids': [], 'zorro_ids': []}
    for line in f:
        system, data = line.split(None, 1)
        lists[system].append(line)
    f.close()

    out = open(os.path.join(dest_dir, 'eisa.list'), 'w')
    out.writelines(lists['eisa_ids'])
    out.flush()
    out.close()

    out = open(os.path.join(dest_dir, 'pci.list'), 'w')
    out.writelines(lists['pci_ids'] + lists['pci_class_ids'])
    out.flush()
    out.close()

    out = open(os.path.join(dest_dir, 'usb.list'), 'w')
    out.writelines(lists['usb_ids'] + lists['usb_class_ids'])
    out.flush()
    out.close()

    out = open(os.path.join(dest_dir, 'zorro.list'), 'w')
    out.writelines(lists['zorro_ids'])
    out.flush()
    out.close()


#
# main
#

if __name__ == "__main__":

    usage = "Usage: %prog [options] pci.ids usb.ids eisa.ids zorro.ids"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, dbfile="ids", sql=False, versioned=False, timed_logs=False)
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
    options_, args_ = parser.parse_args()

    if len(args_) != 4:
        parser.error("needed exactly 4 files: pci.ids usb.ids eisa.ids zorro.ids")

    options_.versioned = False
    make(options_, args_)
