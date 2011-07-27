#!/bin/bash

#: utils/hot-cache.sh : ask to the webserver the pages (to build the cache)
#
#  Copyright (c) 2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 


cd "$HOME/cateee.net/lkddb/web-lkddb"

for page in `echo *.html` ; do
     echo -n "$PAGE"
     wget -q --header="Accept-encoding: gzip" "http://cateee.net/lkddb/web-lkddb/$page" -O /dev/null
done
echo "."

