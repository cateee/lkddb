#!/bin/bash
#: utils/rebuild-web.sh : rebuild web pages and distribute them
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 


set -e

datadir="$HOME/lkddb"
DESTDIR="$HOME/cateee.net"

changeddir="$datadir/changes/changed"
diffdir="$datadir/changes/diff"
newdir="$datadir/changes/new"

destsrc="$HOME/cateee.net/sources"
destweb="$HOME/cateee.net/lkddb/web-lkddb"


[ -d "$datadir/changes" ] || mkdir "$datadir/changes"
[ -d "$changeddir" ] || mkdir "$changeddir"
[ -d "$diffdir" ] || mkdir "$diffdir"
[ -d "$newdir" ] || mkdir "$newdir"


# copy_changed filename orig dest
copy_changed() {
    if [ -f "$3/$1" ] ; then
        if ! cmp -s "$2/$1" "$3/$1" ; then
            cp -p "$3/$1" "$changeddir"
            diff -u "$3/$1" "$2/$1" > "$diffdir/$1.diff" || true
            cp -p "$2/$1" "$3/" ;  echo -n "$1 "
        fi
    else
        cp -p "$2/$1" "$newdir"
        cp -p "$2/$1" "$3/" ;  echo -n "!$1 "
    fi
}


# --- build web pages

echo "=== generating web pages."
make web


# --- distribute the files
echo "=== distribution web pages."
(   cd web-out
    for f in *.html ; do
        copy_changed "$f" "$datadir/web-out" "$destweb"
    done
    echo
)

# --- sources
echo "=== distribute sources."
make tar
cd dist ;
f=`echo lkddb-20??-??-??.tar.gz`
cd ..
copy_changed "$f" "dist" "$destsrc/lkddb-sources"
echo

echo "=== distribute lists ."
lastlist="`ls *.list | tail -1`"
cat "$lastlist" | grep -v '^#' | cut -d ' ' -f 1 | sort | uniq -c | sort -n > dist/counts
echo >> dist/counts
echo "TOTAL: `wc -l < "$lastlist"`" >> dist/counts

cp -p ids.list dist/ids.list
bzip2 -kf -9 dist/ids.list
gzip -cf -9 dist/ids.list > dist/ids.list.gz

cp -p "$lastlist" dist/lkddb.list
bzip2 -kf -9 dist/lkddb.list
gzip -cf -9 dist/lkddb.list > dist/lkddb.list.gz

cd dist
for f in ids.list ids.list.bz2 ids.list.gz lkddb.list lkddb.list.bz2 lkddb.list.gz counts ; do
    copy_changed "$f" "." "$destsrc/lkddb"
done
echo
cd ..
( cd ~/cateee.net/lkddb ; make )

echo "sitemap notify disabled until stable web version"
#( cd /home/cate/cateee.net/; tools/gen-sitemap-0.9/gen-sitemap --notify )

