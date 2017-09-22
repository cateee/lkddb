#!/bin.sh
#: utils/doall.sh : redo "all" released kernel
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License


set -e


do_kernel() {
    ( cd "/home/cate/kernel/linux-2.6" ; git checkout "$1" ; git clean -d -f -f )
    time python ./build-lkddb.py -v -b lkddb -l lkddb-%.log -k ~/kernel/linux-2.6/
}


do_kernel 'master'

do_kernel 'v2.6.12'
do_kernel 'v2.6.13'
do_kernel 'v2.6.14'
do_kernel 'v2.6.15'
do_kernel 'v2.6.16'
do_kernel 'v2.6.17'
do_kernel 'v2.6.18'
do_kernel 'v2.6.19'
do_kernel 'v2.6.20'
do_kernel 'v2.6.21'
do_kernel 'v2.6.22'
do_kernel 'v2.6.23'
do_kernel 'v2.6.24'
do_kernel 'v2.6.25'
do_kernel 'v2.6.26'
do_kernel 'v2.6.27'
do_kernel 'v2.6.28'
do_kernel 'v2.6.29'
do_kernel 'v2.6.30'
do_kernel 'v2.6.31'
do_kernel 'v2.6.32'
do_kernel 'v2.6.33'
do_kernel 'v2.6.34'
do_kernel 'v2.6.35'
do_kernel 'v2.6.36'
do_kernel 'v2.6.37'
do_kernel 'v2.6.38'
do_kernel 'v2.6.39'

( cd "/home/cate/kernel/linux-2.6.git" ; git checkout master )

