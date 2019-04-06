#!/bin/bash
#: utils/rebuild-web.sh : check and copy to webserver the modified pages
#
#  Copyright (c) 2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 

set -e

: ${DATA:='data'}

basedir="$HOME/lkddb"
datadir="$basedir/$DATA"
DESTDIR="/var/www/cateee.net"

changeddir="$datadir/changes/changed"
diffdir="$datadir/changes/diff"
newdir="$datadir/changes/new"

destsrc="/var/www/cateee.net/sources"
destweb="/var/www/cateee.net/lkddb/web-lkddb"

cd "$basedir"

[ -d "$datadir/changes" ] || mkdir "$datadir/changes"
[ -d "$changeddir" ] || mkdir "$changeddir"
[ -d "$diffdir" ] || mkdir "$diffdir"
[ -d "$newdir" ] || mkdir "$newdir"


# copy_changed filename orig dest
check_copy_changed() {
    if [ -f "$3/$1" ] ; then
        if ! cmp -s "$datadir/$2/$1" "$3/$1" ; then
            cp -pf "$3/$1" "$changeddir"
            diff -u "$3/$1" "$datadir/$2/$1" > "$diffdir/$1.diff" || true
            cp -pf "$datadir/$2/$1" "$3/"
	    echo -n "$1 "
	    return 0
	else
	    return 1
        fi
    else
        cp -pf "$datadir/$2/$1" "$newdir"
        cp -pf "$datadir/$2/$1" "$3/"
	echo -n "!$1 "
	return 0
    fi
}
copy_changed() {
    check_copy_changed "$1" "$2" "$3" || true
}


# copy_zip_changed filename dest1 webdest
copy_zip_changed() {
    cp -p "$datadir/$1" "$datadir/$2/$1"
    if check_copy_changed "$1" "$2" "$3" ; then
        bzip2 -kf -9 "$datadir/$2/$1"
        gzip -cf -9 "$datadir/$2/$1" > "$datadir/$2/$1.gz"
	copy_changed "$1.bz2" "$2" "$3"
	copy_changed "$1.gz" "$2" "$3"
    fi
}


# --- build web pages

echo "=== generating web pages."
make web "data=$datadir"


# --- distribute the files
echo "=== distribution web pages."
cd "$datadir/web-out"
for f in *.html ; do
    copy_changed "$f" web-out "$destweb"
done
echo
cd "$basedir"

# --- sources
echo "=== distribute sources."
make tar "data=$datadir"
cd "$datadir/dist" ;
f=`echo lkddb-sources-20??-??-??.tar.gz`
cd "$basedir"
copy_changed "$f" "$datadir/dist" "$destsrc/lkddb-sources"
echo

echo "=== distribute lists."
cd "$datadir"
lastlist="`ls -t lkddb-[234567]*.list | head -1`"
cd "$basedir"
echo "last is $lastlist"
cat "$datadir/$lastlist" | grep -v '^#' | cut -d ' ' -f 1 | sort | uniq -c | sort -n > "$datadir/"dist/counts
echo >> "$datadir/"dist/counts
echo "TOTAL: `wc -l < "$datadir/$lastlist"`" >> "$datadir/"dist/counts

copy_zip_changed ids.list dist "$destsrc/lkddb"
cp "$datadir/$lastlist" "$datadir/"lkddb.list
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
copy_changed "$lastlist" . "$destsrc/lkddb"

echo
cd "$basedir"

echo "=== updating web."

[ -f "$DESTDIR/lkddb/Makefile" ] && ( cd "$DESTDIR/lkddb" ; make )

[ -x "$DESTDIR/"tools/gen-sitemap-0.9/gen-sitemap ] && ( cd "$DESTDIR"; tools/gen-sitemap-0.9/gen-sitemap --notify )

