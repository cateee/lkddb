#!/bin/bash
#: utils.sh : few utilities for developers
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details


# 'clean': remove some working files
# 'tar': create a tar archive ready to be distributed
# 'print': search for active "print" statements (should be used only for debugging)
# 'todo': search for TODOs and incomplete code
# 'diff': compare output of new and old lkddb


set -e

function copy_to_dist() {
    dest="dist/lkddb-$1"
    ! [ -d dist.old ] || rm -fR dist.old
    ! [ -d dist ] || mv dist dist.old
    mkdir dist "$dest"

    for dir in lkddb lkddb/tables lkddb/linux lkddb/ids ; do
        mkdir  "$dest/$dir"
        cp -p "$dir"/*py "$dest/$dir/"
    done
    cp -p lkddb/DESIGN "$dest/lkddb/"

    mkdir "$dest/templates"
    cp -p templates/*.html "$dest/templates/"

    cp *.py *.sh Makefile Manifest TODO "$dest/"

    mkdir "$dest/web-out"

    find . -name '.git' -prune -o -name 'web-out' -prune -o -name 'lkddb-*' -prune -o -name 'dist' -prune -o -name 'dist.old' -prune -o \( \! -name '*.ids' \! -name '*.ids.bz2' \! -name '*.list' \! -name '*.data' \! -name '*.log' \! -name '*.tmp' -print \) > dist/ls.orig
    cd dist/lkddb-20* ; find . -name '.git' -prune -o -name 'web-out' -prune -o \( \! -name '*.ids' \! -name '*.list'  \! -name '*.data'  \! -name '*.log'  \! -name '*.tmp' -print \) > ../../dist/ls.dist ; cd ../..
    if diff --unified=0 dist/ls.orig dist/ls.dist ; then
        true
    else
        exit 1
    fi
}


function copy_to_dist-web() {
    mkdir dist/web
    cp -p web-out/*.html dist/web/
}


case "$1" in

    'clean' )   find . -name '*.pyc' -delete
		rm -Rf a b d
    ;;

    'tar' )     date="$(date --rfc-3339=date)"
		copy_to_dist "$date"
		cd dist
		tar cf ../../lkddb-"$date".tar lkddb-"$date"
		gzip -9 ../../lkddb-"$date".tar
		cd ..
    ;;

    'print' )   find . -name '*.py' | xargs grep '[^#.]print'
    ;;

    'todo' )	find . -name '*.py' | xargs grep -Er '([#?!]{3,}|[^.]print)' *.py
    ;;

esac


