#!/bin/bash
#: utils/utils.sh : few utilities for developers
#
#  Copyright (c) 2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

# distribution:
# - 'tar': create a tar archive ready to be distributed
# - 'web': distribute the web files (copying only the modified files)
# code check:
# - 'print': search for active "print" statements (should be used only for debugging)
# - 'todo': search for TODOs and incomplete code

set -e

: ${DATA:='data'}

function copy_to_dist() {
    dest="$DATA/dist/lkddb-sources-$1"
    mkdir "$dest"

    for dir in `sed -ne 's#^\(.*\)/[^/]*$#\1#p' Manifest | sort -u` ; do
	mkdir "$dest/$dir"
    done

    for f in `cut -d: -f1 Manifest` ; do
        cp -p "$f" "$dest/$f"
    done

    mkdir "$dest/web-out"

    find . -name '.git' -prune -o -name 'data*' -prune -o -name 'web-out' -prune -o -name 'dist' -prune -o -name 'dist.old' -prune -o -name 'changes' -o -name '*.swp' -prune -o -name 'tmp' -prune -o -name '__pycache__' -prune -o \( \! -name '*.ids' \! -name '*.ids.bz2' \! -name '*.list' \! -name '*.data' \! -name '*.log' \! -name 'log' \! -name '*.pyc' \! -name '*.tmp' -print \) > "$DATA/"dist/ls.orig
    ( cd data/dist/lkddb-sources-20??-??-?? ; find . -name '.git' -prune -o -name 'web-out' -prune -o \( \! -name '*.ids' \! -name '*.list'  \! -name '*.data'  \! -name '*.log' \! -name 'log' \! -name '*.tmp' -print \) ) > "$DATA/"dist/ls.dist
    if diff --unified=0 "$DATA/"dist/ls.orig "$DATA/"dist/ls.dist ; then
        true
    else
        echo 'A file is missing in tar: check Makefile source files'
        exit 1
    fi
}


function copy_to_dist-web() {
    mkdir "$DATA/"dist/web
    cp -p "$DATA/"web-out/*.html "$DATA/"dist/web/
}


function counts() {
    echo "$1 __file" > "$1.counts"
    cat "$1" | grep -v '^#' | cut -d ' ' -f 1 | sort | uniq -c >> "$1.counts"
    echo "`wc -l < $1` TOTAL" >> "$1.counts"
}


case "$1" in

    'tar' )
        date="$(date --rfc-3339=date)"
        [[ -d "$DATA/"dist.old ]] && rm -Rf "$DATA/"dist.old
        [[ -d "$DATA/"dist ]] && mv "$DATA/"dist "$DATA/"dist.old
        mkdir "$DATA"/dist
        copy_to_dist "$date"
		if [[ -d "$DATA/"dist.old/lkddb-sources-20??-??-?? ]] ; then
            ( cd "$DATA/"dist.old ; prev=`echo lkddb-sources-20??-??-??` ) ;
		else
		    prev="lkddb-sources-0000-00-00"
		fi
		if diff -ur "$DATA/dist.old/$prev" "$DATA/dist/lkddb-sources-$date" > "$DATA/dist/$prev--$date.diff" ; then
		    echo "No differences since $prev"
		    rm -Rf "$DATA/"dist
		    mv "$DATA/"dist.old "$DATA/"dist
		else
		    (   cd "$DATA/"dist
		        tar cf lkddb-sources-"$date".tar lkddb-sources-"$date"
		        gzip -9 lkddb-sources-"$date".tar
            )
		fi
    ;;
    'count' )
        if [[ -n "$2" ]] ; then
            counts "$2"
        else
            counts "$DATA/"lkddb.list
        fi
    ;;

    'count-all' )
        for f in $DATA/*.list ; do
            counts "$f"
        done
    ;;


    'web' )	copy_to_dist-web
    ;;

    'print' )   find . -name '.git' -prune -o -name 'web-out' -prune -o -name 'dist' -prune -o -name 'dist.old' -prune -o -name 'changes' -prune -o -name '*.py' -print | xargs grep '[^#.]print'
    ;;

    'todo' )	find . -name '.git' -prune -o -name 'web-out' -prune -o -name 'dist' -prune -o -name 'dist.old' -prune -o -name 'changes' -prune -o -name '*.py' -print | xargs grep -Er '([#?!]{3,}|[^.]print)' *.py
    ;;

esac

