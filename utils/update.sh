#!/bin/bash
#: utils/update.sh : update kernel and data
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 


set -e

kdir=/home/cate/kernel/linux/


# --- update sources

(   cd "$kdir"
    git pull --ff-only --no-progress
    git checkout
    [ -d include/config/ ] || mkdir include/config/
    [ -f include/config/auto.conf ] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
)
make check-ids

changed=""

# --- update data files (when necesary)

new=`python utils/check-kernel-version.py "$kdir" . || true`
if [ -n "$new" ] ; then
    echo "=== generating new datafile $new."
    time python ./build-lkddb.py -v -b lkddb -l lkddb-%.log -k ~/kernel/linux-2.6/
    echo build-lkddb.py: DONE
    changed="$changed $new"
fi

[ ! -f ids.data ] || cp -p ids.data ids.data.tmp
make ids.data
if ! cmp -s ids.data ids.data.tmp ; then
    echo "=== a new ids.data was just generated."
    changed="$changed ids.data"
fi


# --- merge and build web pages (when necesary)

if [[ "$changed" =~ "data" ]] ; then
    echo "=== merging lkddb-all.data with: $changed"
    if [ ! -f lkddb-all.data ]; then
	echo "$0 requires an existing lkddb-all.data!" >&2
	echo "please merge some data files before to call $0."
	echo $PWD
	exit 0
    fi
    mv lkddb-all.data lkddb-all.data.tmp
    time python ./merge.py -v -l merge.log -o lkddb-all.data lkddb-all.data.tmp $changed ids.data
fi

bash utils/rebuild-web.sh

