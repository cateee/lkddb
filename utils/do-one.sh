#!/bin/bash
#: utils/doall.sh : redo "all" released kernel
#
#  Copyright (c) 2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License


set -e

kdir="$HOME/kernel"
if [ -n "$2" ] ; then
    data="$2"
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
      [ -d "linux-$1" ] || tar xjf "linux-$1.tar.bz2"
    )
    echo "$kdir/linux-$1"
    build_lkddb "$kdir/linux-$1"
}


if [ -z "$1" ] ;then
    echo 'utils/do-one v5.0 [datadir]   # for tags in git, from 2.6.12'
    echo 'utils/do-one 2.6.9 [datadir]  # for sources in tar archives'
elif [[ "$1" =~ ^v ]] ; then
    do_git_kernel "$1"
    if [[ "$2" != '--skip' ]] ; then
        # restore repository to master
        ( cd "$kdir/linux"
            git checkout master
            git clean -d -f -f
            [ -d include/config/ ] || mkdir include/config/
            [ -f include/config/auto.conf ] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
        )
    fi
else
    do_tar_kernel "$1"
fi

