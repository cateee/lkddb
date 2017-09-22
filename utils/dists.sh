#!/bin/bash
#: utils/dists.sh : distribute (copy to the public web dir) the changed files
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License

ORIGDIR="$HOME/lkddb"
DESTDIR="$HOME/cateee.net"
CHANGESDIR="$ORIGDIR/changes"
CHANGEDDIR="$CHANGESDIR/changed"
DIFFDIR="$CHANGESDIR/diff"
NEWDIR="$CHANGESDIR/new"
DESTSRC="$DESTDIR/sources"
DESTWEB="$DESTDIR/lkddb/web-lkddb"
DATE=`date --rfc-3339=date`

dbs="lkddb.list pci.list usb.list eisa.list zorro.list"
ids="pci.ids usb.ids eisa.ids zorro.ids"

make dists/lkddb-sources-${DATE}.tar.gz dists/lkddb-${DATE}.tar.gz dists/autokernconf-${DATE}.tar.gz

# copy_changed filename orig dest
copy_changed() {
    if [ -f "$3/$1" ] ; then
        if ! cmp -s "$2/$1" "$3/$1" ; then
	    cp -p "$3/$1" "$CHANGEDDIR"
	    diff -u "$3/$1" "$2/$1" > "$DIFFDIR/$1.diff"
	    cp -p "$2/$1" "$3/" ;  echo -n "$1 "
	fi
    else
	cp -p "$2/$1" "$NEWDIR"
        cp -p "$2/$1" "$3/" ;  echo -n "!$1 "
    fi
}

for f in $dbs $ids counts dists/lkddb.list.gz dists/lkddb.list.bz2 dists/lkddb-${DATE}.tar.gz ; do
    copy_changed "`basename $f`" "`dirname $f`" "$DESTSRC/lkddb"
done

copy_changed "lkddb-sources-${DATE}.tar.gz" "$ORIGDIR/dists" "$DESTSRC/lkddb-sources"
copy_changed "autokernconf-${DATE}.tar.gz"  "$ORIGDIR/dists" "$DESTSRC/autokernconf"

( cd web-lkddb
for f in *.html ; do
    copy_changed "$f" "$ORIGDIR/web-lkddb" "$DESTWEB"
done
)
echo

