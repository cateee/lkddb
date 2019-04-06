#!/bin/bash
#: utils/update.sh : update kernel and data
#
#  Copyright (c) 2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 

set -e

: ${DATA:='data'}
kdir="$HOME/kernel/linux/"


# --- update sources

if [[ "$1" = "--skip-update" ]] ; then
    true
elif [[ -n "$1" ]] ; then
    echo "Doing non master branche/tag: '$1'"
(   cd "$kdir"
    git checkout "$1"
    [[ -d include/config/ ]] || mkdir include/config/
    [[ -f include/config/auto.conf ]] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
)
else
(   cd "$kdir"
    git checkout master || true
    git reset --hard
    git pull --ff-only --no-progress || true
    git clean -d -x -f
    git checkout master
    [[ -d include/config/ ]] || mkdir include/config/
    [[ -f include/config/auto.conf ]] || echo "CONFIG_LOCALVERSION_AUTO=y" > include/config/auto.conf
)
make check-ids
fi

changed=""

# --- update data files (when necesary)

new=`python3 utils/check-kernel-version.py "$kdir" "$DATA" || true`
if [[ -n "$new" ]] ; then
    echo "=== generating new datafile $new."
    time python3 ./build-lkddb.py -b "$DATA/"lkddb -l "$DATA/"lkddb-%.log -k ~/kernel/linux/
    echo build-lkddb.py: DONE
    changed="$changed $DATA/$new"
fi

[[ ! -f "$DATA/"ids.data ]] || cp -p "$DATA/"ids.data data/ids.data.tmp
make "$DATA/"ids.data
if ! cmp -s "$DATA/"ids.data "$DATA/"ids.data.tmp ; then
    echo "=== a new ids.data was just generated."
    changed="$changed $DATA/ids.data"
fi


# --- merge and build web pages (when necesary)

if [[ "$changed" =~ "data" ]] ; then
    echo "=== merging lkddb-all.data with: $changed"
    if [[ ! -f "$DATA/"lkddb-all.data ]] ; then
	echo "$0 requires an existing lkddb-all.data!" >&2
	echo "please merge some data files before to call $0."
	echo $PWD
	exit 0
    fi
    mv "$DATA/"lkddb-all.data "$DATA/"lkddb-all.data.tmp
    time python3 ./merge.py -v -l "$DATA/"merge.log -o "$DATA/"lkddb-all.data "$DATA/"lkddb-all.data.tmp $changed "$DATA/"ids.data
fi

bash utils/rebuild-web.sh

