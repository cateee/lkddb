#!/usr/bin/python
#: build-lkddb.py : hardware database generator from linux kernel sources
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import argparse
import logging
import os.path
import sys

import lkddb.linux

logger = logging.getLogger(__name__)


def make(options, kerneldir, dirs):
    tree = lkddb.linux.LinuxKernelTree(lkddb.TASK_BUILD, kerneldir, dirs)
    options.version = tree.get_strversion()
    if options.versioned:
        options.datafile += '-' + options.version
    lkddb.init(options)
    logger.info("=== Scan Linux kernel sources")
    tree.scan_sources()
    logger.info("=== Preparing data")
    tree.finalize_sources()
    logger.info("=== Write data")
    tree.write(data_filename=options.datafile + '.data',
               list_filename=options.datafile + '.list')


#
# main
#

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Scan Linux kernel sources to find supported devices and drivers")
    verbose_group = parser.add_mutually_exclusive_group()
    verbose_group.add_argument('-v', '--verbose',
                               action='count', default=1,
                               help="increase output verbosity")
    verbose_group.add_argument('-q', '--quiet',
                               action='store_const', const=0,
                               help="inhibit messages")
    parser.add_argument('-b', '--base', dest='datafile',
                        action='store', type=str, default='lkddb',
                        help="base FILE name to read and write data", metavar='FILE')
    parser.add_argument('-l', '--log', dest='log_filename',
                        action='store', type=str,
                        help="FILE to put log messages (default to stderr)", metavar='FILE')
    parser.add_argument('-k', '--versioned', dest='versioned',
                        action='store_const', const=True, default=False,
                        help="append version to file names (log and data)")
    parser.add_argument('kernel_dir',
                        help="directory of Linux kernel sources")
    parser.add_argument('sub_dir',
                        action='store', type=str, nargs='*',
                        help="subdirectories of kernel to parse (default: all)")
    args = parser.parse_args()

    kerneldir = os.path.normpath(args.kernel_dir)
    if not os.path.isdir(kerneldir):
        logger.fatal("Error: I could not find directory {}".format(args.kernel_dir))
        sys.exit(1)

    if kerneldir[-1] != '/':
        kerneldir += '/'
    if len(args.sub_dir) > 1:
        dirs = tuple(args.sub_dir[1:])
    else:
        dirs = ('arch', 'block', 'crypto', 'drivers', 'firmware', 'fs', 'init',
                'ipc', 'kernel', 'lib', 'mm', 'net', 'security',
                'sound', 'usr', 'virt')

    make(args, kerneldir, dirs)
