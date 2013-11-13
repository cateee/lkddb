#!/bin/bash
#: utils/rebuild-web.sh : check and copy to webserver the modified pages
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
check_copy_changed() {
    if [ -f "$3/$1" ] ; then
        if ! cmp -s "$2/$1" "$3/$1" ; then
            cp -plf "$3/$1" "$changeddir"
            diff -u "$3/$1" "$2/$1" > "$diffdir/$1.diff" || true
            cp -plf "$2/$1" "$3/"
	    echo -n "$1 "
	    return 0
	else
	    return 1
        fi
    else
        cp -plf "$2/$1" "$newdir"
        cp -plf "$2/$1" "$3/"
	echo -n "!$1 "
	return 0
    fi
}
copy_changed() {
    check_copy_changed "$1" "$2" "$3" || true
}


# copy_zip_changed filename dest1 webdest
copy_zip_changed() {
    cp -p "$1" "$2/$1"
    if check_copy_changed "$1" "$2" "$3" ; then
        bzip2 -kf -9 "$2/$1"
        gzip -cf -9 "$2/$1" > "$2/$1.gz"
	copy_changed "$1.bz2" "$2" "$3"
	copy_changed "$1.gz" "$2" "$3"
    fi
}

# copy_and_zip file dest-dir
copy_and_zip() {
   cp -p "$1" "$2/$1"
   bzip2 -kf -9 "$2/$1"
   gzip -cf -9 "$2/$1" > "$2/$1.gz"
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
f=`echo lkddb-sources-20??-??-??.tar.gz`
cd ..
copy_changed "$f" "dist" "$destsrc/lkddb-sources"
echo

echo "=== distribute lists."
lastlist="`ls -t lkddb-3*.list | head -1`"
echo "last is $lastlist"
cat "$lastlist" | grep -v '^#' | cut -d ' ' -f 1 | sort | uniq -c | sort -n > dist/counts
echo >> dist/counts
echo "TOTAL: `wc -l < "$lastlist"`" >> dist/counts

copy_zip_changed ids.list dist "$destsrc/lkddb"
cp "$lastlist" lkddb.list
copy_zip_changed lkddb.list dist "$destsrc/lkddb"
copy_zip_changed eisa.list dist "$destsrc/lkddb"
copy_zip_changed pci.list dist "$destsrc/lkddb"
copy_zip_changed usb.list dist "$destsrc/lkddb"
copy_zip_changed zorro.list dist "$destsrc/lkddb"
copy_zip_changed eisa.ids dist "$destsrc/lkddb"
copy_zip_changed pci.ids dist "$destsrc/lkddb"
copy_zip_changed usb.ids dist "$destsrc/lkddb"
copy_zip_changed zorro.ids dist "$destsrc/lkddb"

copy_changed counts dist "$destsrc/lkddb"
copy_changed "$lastlist" "." "$destsrc/lkddb"

echo
cd ..

echo "=== updating web."

[ -f ~/cateee.net/lkddb/Makefile ] && ( cd ~/cateee.net/lkddb ; make )

[ -x /home/cate/cateee.net/tools/gen-sitemap-0.9/gen-sitemap ] && ( cd /home/cate/cateee.net/; tools/gen-sitemap-0.9/gen-sitemap --notify )

