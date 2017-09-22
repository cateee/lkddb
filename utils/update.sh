#!/bin/bash
#: update.sh : update kernel and data
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 


set -e

kdir=/home/cate/kernel/linux-2.6/

datadir="$HOME/lkddb"
DESTDIR="$HOME/cateee.net"

changeddir="$datadir/changes/changed"
diffdir="$datadir/changes/diff"
newdir="datadir/changes/new"

DESTSRC="$DESTDIR/sources"
destweb="$HOME/cateee.net/lkddb/web-lkddb"



# copy_changed filename orig dest
copy_changed() {
    if [ -f "$3/$1" ] ; then
        if ! cmp -s "$2/$1" "$3/$1" ; then
            cp -p "$3/$1" "$changeddir"
            diff -u "$3/$1" "$2/$1" > "$diffdir/$1.diff"
            cp -p "$2/$1" "$3/" ;  echo -n "$1 "
        fi
    else
        cp -p "$2/$1" "$newdir"
        cp -p "$2/$1" "$3/" ;  echo -n "!$1 "
    fi
}


# --- update sources

( cd "$kdir" ; git pull --ff-only --no-progress ; git checkout )
make check-ids

changed=""


# --- update data files (when necesary)

new=`check-kernel-version.py "$kdir" .`
if $? ; then
    time python ./build-lkddb.py -v -b lkddb -l lkddb-%.log -k ~/kernel/linux-2.6/
    changed="$changed $new"
fi

cp -p ids.data ids.data.tmp
make ids.data
if ! cmp -s ids.data ids.data.tmp ; then
    changed="$changed ids.data"
fi


# --- merge and build web pages (when necesary)

if [[ "$changed" =~ "data" ]] ; then
    mv lkddb-all.data lkddb-all.data.tmp
    time python ./merge.py -v -l merge.log -o lkddb-all.data lkddb-all.data.tmp ${new} ids.data

    time python ./gen-web-lkddb.py -v -l web.log -f lkddb-all.data templates/ web-out/

# --- distribute the files
    ( cd web-lkddb
      for f in *.html ; do
          copy_changed "$f" "$datadir/web-out" "$destweb"
      done
      echo	
    )

    ( cd /home/cate/cateee.net/; tools/gen-sitemap-0.9/gen-sitemap --notify )
fi

