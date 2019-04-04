#!/bin/bash
#: utils/rebuild-web.sh : check and copy to webserver the modified pages
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 


set -e

datadir="$HOME/lkddb/data"
DESTDIR="/var/www/cateee.net"

changeddir="$datadir/changes/changed"
diffdir="$datadir/changes/diff"
newdir="$datadir/changes/new"

destsrc="/var/www/cateee.net/sources"
destweb="/var/www/cateee.net/lkddb/web-lkddb"


[ -d "$datadir/changes" ] || mkdir "$datadir/changes"
[ -d "$changeddir" ] || mkdir "$changeddir"
[ -d "$diffdir" ] || mkdir "$diffdir"
[ -d "$newdir" ] || mkdir "$newdir"


# copy_changed filename orig dest
check_copy_changed() {
    if [ -f "$3/$1" ] ; then
        if ! cmp -s "$2/$1" "$3/$1" ; then
            cp -pf "$3/$1" "$changeddir"
            diff -u "$3/$1" "$2/$1" > "$diffdir/$1.diff" || true
            cp -pf "$2/$1" "$3/"
	    echo -n "$1 "
	    return 0
	else
	    return 1
        fi
    else
        cp -pf "$2/$1" "$newdir"
        cp -pf "$2/$1" "$3/"
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
lastlist="`ls -t data/lkddb-[34567]*.list | head -1`"
echo "last is $lastlist"
cat "$lastlist" | grep -v '^#' | cut -d ' ' -f 1 | sort | uniq -c | sort -n > dist/counts
echo >> dist/counts
echo "TOTAL: `wc -l < "$lastlist"`" >> dist/counts

copy_zip_changed data/ids.list dist "$destsrc/lkddb"
cp "$lastlist" data/lkddb.list
copy_zip_changed data/lkddb.list dist "$destsrc/lkddb"
copy_zip_changed data/eisa.list dist "$destsrc/lkddb"
copy_zip_changed data/pci.list dist "$destsrc/lkddb"
copy_zip_changed data/usb.list dist "$destsrc/lkddb"
copy_zip_changed data/zorro.list dist "$destsrc/lkddb"
copy_zip_changed data/eisa.ids dist "$destsrc/lkddb"
copy_zip_changed data/pci.ids dist "$destsrc/lkddb"
copy_zip_changed data/usb.ids dist "$destsrc/lkddb"
copy_zip_changed data/zorro.ids dist "$destsrc/lkddb"

copy_changed counts dist "$destsrc/lkddb"
copy_changed "$lastlist" "." "$destsrc/lkddb"

echo
cd ..

echo "=== updating web."

[ -f ~/cateee.net/lkddb/Makefile ] && ( cd ~/cateee.net/lkddb ; make )

[ -x "$HOME"/cateee.net/tools/gen-sitemap-0.9/gen-sitemap ] && ( cd /home/cate/cateee.net/; tools/gen-sitemap-0.9/gen-sitemap --notify )

