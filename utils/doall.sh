#!/bin/sh
#: utils/doall.sh : redo "all" released kernel
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License


set -e

kdir="/home/cate/kernel/"

build_lkddb() {
    time python ./build-lkddb.py -v -b lkddb -l lkddb-%.log -k "$1"
}


do_git_kernel() {
    echo "------ doing $1 --------"
    ( cd "$kdir/linux-2.6"
      git checkout "$1"
      git clean -d -f -f
      [ -d include/config/ ] || mkdir include/config/
      [ -f include/config/auto.conf ] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
    )
    build_lkddb "$kdir/linux-2.6/"
}

do_tar_kernel() {
    echo "------ doing $1 --------"
    ( cd "$kdir"
      [ -d "linux-$1" ] || tar xjf "linux-$1.tar.bz2"
    )
    echo "$kdir/linux-$1"
    build_lkddb "$kdir/linux-$1"
}


if false ; then

do_tar_kernel '2.6.0'
do_tar_kernel '2.6.1'
do_tar_kernel '2.6.2'
do_tar_kernel '2.6.3'
do_tar_kernel '2.6.4'
do_tar_kernel '2.6.5'
do_tar_kernel '2.6.6'
do_tar_kernel '2.6.7'
do_tar_kernel '2.6.8'
do_tar_kernel '2.6.9'
do_tar_kernel '2.6.10'
do_tar_kernel '2.6.11'

do_git_kernel 'v2.6.12'
do_git_kernel 'v2.6.13'
do_git_kernel 'v2.6.14'
do_git_kernel 'v2.6.15'
do_git_kernel 'v2.6.16'
do_git_kernel 'v2.6.17'
do_git_kernel 'v2.6.18'
do_git_kernel 'v2.6.19'
do_git_kernel 'v2.6.20'
do_git_kernel 'v2.6.21'
do_git_kernel 'v2.6.22'
do_git_kernel 'v2.6.23'
do_git_kernel 'v2.6.24'
do_git_kernel 'v2.6.25'
do_git_kernel 'v2.6.26'
do_git_kernel 'v2.6.27'
fi
do_git_kernel 'v2.6.28'
do_git_kernel 'v2.6.29'
do_git_kernel 'v2.6.30'
do_git_kernel 'v2.6.31'
do_git_kernel 'v2.6.32'
do_git_kernel 'v2.6.33'
do_git_kernel 'v2.6.34'
do_git_kernel 'v2.6.35'
do_git_kernel 'v2.6.36'
do_git_kernel 'v2.6.37'
do_git_kernel 'v2.6.38'
do_git_kernel 'v2.6.39'
#fi

do_git_kernel 'v3.0'

#HEAD
do_git_kernel 'master'

