#!/usr/bin/python
#: ids_importer.py : import ids
#
#  Copyright (c) 2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import argparse
import logging
import os.path

import lkddb
import lkddb.ids

logger = logging.getLogger(__name__)


def make(options):
    tree = lkddb.ids.IdsTree(lkddb.TASK_BUILD,
                             args.pci_ids, args.usb_ids,
                             args.eisa_ids, args.zorro_ids)
    options.version = tree.get_strversion()
    lkddb.init(options)
    logger.info("=== Read 'ids' files")
    tree.scan_sources()
    logger.info("=== Preparing data")
    tree.finalize_sources()
    logger.info("=== Write data")
    tree.write(data_filename=options.datafile + ".data",
               list_filename=options.datafile + ".list")
    dest_dir = os.path.dirname(options.datafile)
    build_single_ids(options.datafile + ".list", dest_dir)


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
    parser = argparse.ArgumentParser(
        description="Transform files from `ids` format to `list` format"
    )
    verbose_group = parser.add_mutually_exclusive_group()
    verbose_group.add_argument("-v", "--verbose",
                               action="count", default=1,
                               help="increase output verbosity")
    verbose_group.add_argument("-q", "--quiet",
                               action="store_const", const=0,
                               help="inhibit messages")
    parser.add_argument("-b", "--base", dest="datafile",
                        action="store", type=str,
                        help="base FILE name to read and write data", metavar="FILE")
    parser.add_argument("-l", "--log", dest="log_filename",
                        action="store", type=str,
                        help="FILE to put log messages (default to stderr)", metavar="FILE")
    parser.add_argument('pci_ids',  # dest='pci_ids',
                        help="path of the pci.ids data")
    parser.add_argument('usb_ids',  # dest='usb_ids',
                        help="path of the usb.ids data")
    parser.add_argument('eisa_ids',  # dest='eisa_ids',
                        help="path of the eisa.ids data")
    parser.add_argument('zorro_ids',  # dest='zorro_ids',
                        help="path of the zorro.ids data")
    args = parser.parse_args()

    make(args)
