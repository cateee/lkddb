#!/usr/bin/make -f
#: Makefile : rules to make, distribute and test lkddb
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details


# --- configuration ---

# Note these option could be given in command line: e.g.:

#  $ make all kdir=/pub/linux-3.0/linux-3.0.0

# kernel directory
kdir ?= ~/kernel/linux-2.6/


# --- generic rules ---

all: Manifest lkddb web-out/index.html
.PHONY: lkddb chars merge web clean tests tar Manifest


# --- generic definitions ---

DATE = $(shell date --rfc-3339=date)
datafiles = lkddb-[23].*.data 
sources = *.py */*.py */*/*.py templates/*.html Makefile utils.sh TODO lkddb/DESIGN

# --- building lists ---

lkddb:
	time python ./build-lkddb.py -vv -b lkddb -l lkddb-%.log -k ~/kernel/linux-2.6/

merge: lkddb-all.data
lkddb-all.data: ids.data ${datafiles}
	time python ./merge.py -v -l merge.log -o lkddb-all.data ${datafiles} ids.data

web: web-out/index.html
web-out/index.html: lkddb-all.data templates/*.html
	time python ./gen-web-lkddb.py -v -l web.log -f lkddb-all.data templates/ web-out/

pci.ids:
	wget http://pciids.sourceforge.net/v2.2/pci.ids.bz2
	bzip2 -d pci.ids.bz2
usb.ids:
	wget http://www.linux-usb.org/usb.ids.bz2
	bzip2 -d usb.ids.bz2
eisa.ids: ${kdir}/drivers/eisa/eisa.ids
	cp ${kdir}/drivers/eisa/eisa.ids .
zorro.ids: ${kdir}/drivers/zorro/zorro.ids
	cp ${kdir}/drivers/zorro/zorro.ids .

ids.data: pci.ids usb.ids eisa.ids zorro.ids
	time python ./ids_importer.py -v -b ids -l ids.log  pci.ids usb.ids eisa.ids zorro.ids


# --- distributing ---

clean:
	find . -name '*.pyc' -delete
	-rm -f Manifest *.ids *.list *.data *.log
	-rm -f web-out/*.html

tar: Manifest
	./utils.sh tar

Manifest: ${sources} Makefile utils.sh
	echo Manifest : "Manifest file" > Manifest ; \
	for f in `find -name '*.py'` Makefile utils.sh ; do \
	    echo $$f :  `head -3 $$f | sed -ne 's/^#:[^:]*:[ ]*\(.*\)$$/\1/p' -` >> Manifest ; \
	done
	echo 

