#!/bin/bash
#: update.sh : update kernel and data
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details
#  or distributable with any GNU Documentation Public License 


set -e

( cd /home/cate/kernel/linux-2.6/ ; git pull --ff-only --no-progress ; git checkout )
make check-ids

make lkddb

make web

bash ./dists.sh

( cd /home/cate/cateee.net/; tools/gen-sitemap-0.9/gen-sitemap --notify )

