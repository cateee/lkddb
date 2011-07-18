#!/bin/bash

set -e

( cd /home/cate/kernel/linux-2.6/ ; git pull ; git checkout )
##kver="$(/home/cate/kernel/linux-2.6/)"

make check-ids

make lkddb

make web

bash ./dists.sh

( cd /home/cate/cateee.net/; tools/gen-sitemap-0.9/gen-sitemap --notify )

