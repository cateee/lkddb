#!/bin/bash
#: utils/utils.sh : few utilities for developers
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

# distribution:
# - 'tar': create a tar archive ready to be distributed
# - 'web': distribute the web files (copying only the modified files)
# code check:
# - 'print': search for active "print" statements (should be used only for debugging)
# - 'todo': search for TODOs and incomplete code


set -e

function copy_to_dist() {
    dest="dist/lkddb-sources-$1"
    mkdir "$dest"

    for dir in `sed -ne 's#^\(.*\)/[^/]*$#\1#p' Manifest | sort -u` ; do
	mkdir "$dest/$dir"
    done

    for f in `cut -d: -f1 Manifest` ; do
        cp -p "$f" "$dest/$f"
    done

    mkdir "$dest/web-out"

    find . -name '.git' -prune -o -name 'data*' -prune -o -name 'web-out' -prune -o -name 'dist' -prune -o -name 'dist.old' -prune -o -name 'changes' -prune -o -name 'tmp' -prune -o -name '__pycache__' -prune -o \( \! -name '*.ids' \! -name '*.ids.bz2' \! -name '*.list' \! -name '*.data' \! -name '*.log' \! -name 'log' \! -name '*.pyc' \! -name '*.tmp' -print \) > dist/ls.orig
    cd dist/lkddb-sources-20??-??-?? ; find . -name '.git' -prune -o -name 'web-out' -prune -o \( \! -name '*.ids' \! -name '*.list'  \! -name '*.data'  \! -name '*.log' \! -name 'log' \! -name '*.tmp' -print \) > ../../dist/ls.dist ; cd ../..
    if diff --unified=0 dist/ls.orig dist/ls.dist ; then
        true
    else
        echo 'A file is missing in tar: check Makefile source files'
        exit 1
    fi
}


function copy_to_dist-web() {
    mkdir dist/web
    cp -p web-out/*.html dist/web/
}


case "$1" in

    'tar' )     date="$(date --rfc-3339=date)"
	    	[ -d dist.old ] && rm -Rf dist.old
    		[ -d dist ] && mv dist dist.old
    		mkdir dist
		copy_to_dist "$date"
		if [ -d dist.old/lkddb-sources-20??-??-?? ] ; then
		    cd dist.old ; prev=`echo lkddb-sources-20??-??-??` ; cd ..
		else
		    prev="lkddb-sources-0000-00-00"
		fi
		if diff -ur "dist.old/$prev" $"dist/lkddb-sources-$date" > "dist/$prev--$date.diff" ; then
		    echo "No differences since $prev"
		    rm -Rf dist
		    mv dist.old dist
		else
		    cd dist
		    tar cf lkddb-sources-"$date".tar lkddb-sources-"$date"
		    gzip -9 lkddb-sources-"$date".tar
		    cd ..
		fi
    ;;
    'web' )	copy_to_dist-web
    ;;

    'print' )   find . -name '.git' -prune -o -name 'web-out' -prune -o -name 'dist' -prune -o -name 'dist.old' -prune -o -name 'changes' -prune -o -name '*.py' -print | xargs grep '[^#.]print'
    ;;

    'todo' )	find . -name '.git' -prune -o -name 'web-out' -prune -o -name 'dist' -prune -o -name 'dist.old' -prune -o -name 'changes' -prune -o -name '*.py' -print | xargs grep -Er '([#?!]{3,}|[^.]print)' *.py
    ;;

esac


