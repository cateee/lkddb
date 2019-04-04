#!/bin/sh
#: utils/doall.sh : redo "all" released kernel
#
#  Copyright (c) 2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License


set -e

echo 'utils/do-all [datadir]'

kdir="$HOME/kernel"

if [ -n "$1" ] ; then
    data="$1"
else
    data='data'
fi

[ -d "$data" ] || mkdir "$data"

build_lkddb() {
    time python3 ./build-lkddb.py -b "$data/"lkddb -l "$data/"lkddb-%.log -k "$1"
}


do_git_kernel() {
    echo "------ doing $1 --------"
    ( cd "$kdir/linux"
      git checkout "$1"
      git clean -d -f -f
      [ -d include/config/ ] || mkdir include/config/
      [ -f include/config/auto.conf ] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
    )
    build_lkddb "$kdir/linux"
}

do_tar_kernel() {
    echo "------ doing $1 --------"
    ( cd "$kdir"
      [ -d "linux-$1" ] || extract_tar "$1"
    )
    echo "$kdir/linux-$1"
    build_lkddb "$kdir/linux-$1"
}

extract_tar() {
    # we use this function, because some old kernels put files in a non version linux/ directory
    rm -Rf tmp
    mkdir tmp
    cd tmp
    tar xjf "../linux-$1.tar.bz2"
    cd ..
    mv tmp/linux* linux-$1
}

do_tar_kernel '2.5.45'
do_tar_kernel '2.5.46'
do_tar_kernel '2.5.47'
do_tar_kernel '2.5.48'
do_tar_kernel '2.5.49'
do_tar_kernel '2.5.50'
do_tar_kernel '2.5.51'
do_tar_kernel '2.5.52'
do_tar_kernel '2.5.53'
do_tar_kernel '2.5.54'
do_tar_kernel '2.5.55'
do_tar_kernel '2.5.56'
do_tar_kernel '2.5.57'
do_tar_kernel '2.5.58'
do_tar_kernel '2.5.59'
do_tar_kernel '2.5.60'
do_tar_kernel '2.5.61'
do_tar_kernel '2.5.62'
do_tar_kernel '2.5.63'
do_tar_kernel '2.5.64'
do_tar_kernel '2.5.65'
do_tar_kernel '2.5.66'
do_tar_kernel '2.5.67'
do_tar_kernel '2.5.68'
do_tar_kernel '2.5.69'
do_tar_kernel '2.5.70'
do_tar_kernel '2.5.71'
do_tar_kernel '2.5.72'
do_tar_kernel '2.5.73'
do_tar_kernel '2.5.74'
do_tar_kernel '2.5.75'

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

do_git_kernel 'v3.0'
do_git_kernel 'v3.1'
do_git_kernel 'v3.2'
do_git_kernel 'v3.3'
do_git_kernel 'v3.4'
do_git_kernel 'v3.5'
do_git_kernel 'v3.6'
do_git_kernel 'v3.7'
do_git_kernel 'v3.8'
do_git_kernel 'v3.9'
do_git_kernel 'v3.10'
do_git_kernel 'v3.11'
do_git_kernel 'v3.12'
do_git_kernel 'v3.13'
do_git_kernel 'v3.14'
do_git_kernel 'v3.15'
do_git_kernel 'v3.16'
do_git_kernel 'v3.17'
do_git_kernel 'v3.18'
do_git_kernel 'v3.19'

do_git_kernel 'v4.0'
do_git_kernel 'v4.1'
do_git_kernel 'v4.2'
do_git_kernel 'v4.3'
do_git_kernel 'v4.4'
do_git_kernel 'v4.5'
do_git_kernel 'v4.6'
do_git_kernel 'v4.7'
do_git_kernel 'v4.8'
do_git_kernel 'v4.9'
do_git_kernel 'v4.10'
do_git_kernel 'v4.11'
do_git_kernel 'v4.12'
do_git_kernel 'v4.13'
do_git_kernel 'v4.14'
do_git_kernel 'v4.15'
do_git_kernel 'v4.16'
do_git_kernel 'v4.17'
do_git_kernel 'v4.18'
do_git_kernel 'v4.19'
do_git_kernel 'v4.20'

do_git_kernel 'v5.0'

#HEAD
do_git_kernel 'master'

# Merging
echo 'merging *.data'
rm -f "$data/"lkddb-all.data
time python3 ./merge.py -l "$data/"merge.log -o "$data/"lkddb-all.data "$data/"lkddb-2.6.?.data "$data/"lkddb-2.6.??.data "$data/"lkddb-3.?.data "$data/"lkddb-3.??.data "$data/"lkddb-4.?.data "$data/"lkddb-4.??.data "$data/"lkddb-5.?.data "$data/"ids.data
