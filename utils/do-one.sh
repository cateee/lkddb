#!/bin/bash
#: utils/doall.sh : redo "all" released kernel
#
#  Copyright (c) 2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License

set -e

: ${DATA:='data'}
: ${KDIR:="$HOME/kernel"}

if [[ -z "$1" ]] ; then
    echo '[DATA="data"] utils/do-one v5.0    # for tags in git, from 2.6.12'
    echo '[DATA="data"] utils/do-one 2.6.9   # for sources in tar archives'
    exit 0
else
    echo "doing $1, from '$KDIR' to '$DATA'"
fi


[[ -d "$DATA" ]] || mkdir "$DATA"

build_lkddb() {
    time python3 ./build-lkddb.py -b "$DATA/"lkddb -l "$DATA/"lkddb-%.log -k "$1"
}

do_git_kernel() {
    echo "------ doing $1 --------"
    ( cd "$KDIR/linux"
      git checkout "$1"
      git clean -d -f -f
      [[ -d include/config/ ]] || mkdir include/config/
      [[ -f include/config/auto.conf ]] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
    )
    build_lkddb "$KDIR/linux"
}

do_tar_kernel() {
    echo "------ doing $1 --------"
    ( cd "$KDIR"
      [[ -d "linux-$1" ]] || extract_tar $1
    )
    echo "$KDIR/linux-$1"
    build_lkddb "$KDIR/linux-$1"
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

if [[ "$1" =~ ^v ]] ; then
    do_git_kernel "$1"
    if [[ "$2" != '--skip' ]] ; then
        # restore repository to master
        ( cd "$KDIR/linux"
            git checkout master
            git clean -d -f -f
            [[ -d include/config/ ]] || mkdir include/config/
            [[ -f include/config/auto.conf ]] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
        )
    fi
else
    do_tar_kernel "$1"
fi

