#!/usr/bin/python
#: merge.py : merge data from different version into a big database
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import argparse
import logging

import lkddb
import lkddb.linux
import lkddb.ids

logger = logging.getLogger(__name__)


def make(options):

    lkddb.init(options)

    linux_tree = lkddb.linux.LinuxKernelTree(lkddb.TASK_CONSOLIDATE, None, [])
    ids_tree = lkddb.ids.IdsTree(lkddb.TASK_CONSOLIDATE, None, None, None, None)
    storage = lkddb.Storage((linux_tree, ids_tree))

    logger.info("=== Read files to consolidate")

    for f in options.input_file:
        storage.read_data(f)

        logger.info("=== Write consolidate main file")
    storage.write_data(filename=options.consolidated)


#
# main
#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Merge different lkddb data (one per version) into a single file"
    )
    verbose_group = parser.add_mutually_exclusive_group()
    verbose_group.add_argument("-v", "--verbose",
                               action="count", default=1,
                               help="increase output verbosity")
    verbose_group.add_argument("-q", "--quiet",
                               action="store_const", const=0,
                               help="inhibit messages")
    parser.add_argument("-o", "--output", dest="consolidated",
                        action="store", type=str,
                        help="base FILE name to read and write data", metavar="FILE")
    parser.add_argument("-l", "--log", dest="log_filename",
                        action="store", type=str,
                        help="FILE to put log messages (default is stderr)", metavar="FILE")
    parser.add_argument('input_file',
                        action='store', type=str, nargs='+',
                        help="original LKDDb file")
    args = parser.parse_args()

    make(args)
