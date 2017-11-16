#!/usr/bin/make -f
#: Makefile : rules to make, distribute and test lkddb
#
#  Copyright (c) 2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details


# --- configuration ---

# Note these option could be given in command line: e.g.:

#  $ make all kdir=/pub/linux-3.0/linux-3.0.0

# kernel directory
kdir ?= ~/kernel/linux/


# --- generic rules ---

all: Manifest lkddb web-out/index.html
.PHONY: lkddb merge web check-ids check-pci.ids check-usb.ids check-eisa.ids check-zorro.ids clean tests tar Manifest


# --- generic definitions ---

datafiles ?= $(shell bash -O nullglob -c "echo lkddb-2.6.?.data lkddb-2.6.??.data lkddb-3.?.data lkddb-3.??.data lkddb-4.?.data lkddb-4.??.data lkddb-5.?.data lkddb-5.??.data")
my_sources = *.py lkddb/*.py lkddb/*/*.py templates/*.html utils/*.py utils/*.sh Makefile TODO lkddb/DESIGN
all_sources = ${my_sources} GPL-2 GPL-3

# --- information and debug targers ---

listdata:
	@echo ${datafiles}

# --- clean targets ---

clean:
	-find . -name '*.pyc' -delete
	-rm -f Manifest *.ids *.ids.bz2 *.list *.data *.log *.tmp
	-rm -f web-out/*.html

mrproper: clean
	-rm -f web-out/*
	-rm -Rf dist dist.old changes

# --- building lists ---

lkddb:
	time python3 ./build-lkddb.py -v -b lkddb -l lkddb-%.log -k ${kdir}

merge: lkddb-all.data
lkddb-all.data: ids.data ${datafiles} merge.py
	[ ! -f lkddb-all.data ] || mv lkddb-all.data lkddb-all.data.tmp
	time python3 ./merge.py -v -l merge.log -o lkddb-all.data lkddb-all.data.tmp ${datafiles} ids.data

web: web-out/index.html
web-out/index.html: lkddb-all.data templates/*.html gen-web-lkddb.py
	time python3 ./gen-web-lkddb.py -v -l web.log -f lkddb-all.data templates/ web-out/


# These targets require extern files
# We download files only with explicit user agreement (e.g. "make check-ids")

check-pci.ids:
	wget -N https://pci-ids.ucw.cz/v2.2/pci.ids.bz2
	bzip2 -kfd pci.ids.bz2
check-usb.ids:
	wget -N http://www.linux-usb.org/usb.ids.bz2
	bzip2 -kfd usb.ids.bz2
check-eisa.ids: ${kdir}/drivers/eisa/eisa.ids
	cp ${kdir}/drivers/eisa/eisa.ids .
check-zorro.ids: ${kdir}/drivers/zorro/zorro.ids
	cp ${kdir}/drivers/zorro/zorro.ids .
check-ids: check-pci.ids check-usb.ids check-eisa.ids check-zorro.ids

ids.data: pci.ids usb.ids eisa.ids zorro.ids
	@if ! [ -f pci.ids -a -f usb.ids -a -f eisa.ids -a -f zorro.ids ] ; then \
	    echo "Missing one ids file."; echo "Run 'make check-ids' to download the needed files"; exit 1; \
	fi
	time python3 ./ids_importer.py -v -b ids -l ids.log  pci.ids usb.ids eisa.ids zorro.ids


# --- distributing ---

tar: Manifest
	./utils/utils.sh tar

Manifest: ${all_sources}
	@: > Manifest ; \
	echo "GPL-2 : GNU General Public License, version 2" >> Manifest ; \
	echo "GPL-3 : GNU General Public License, version 3" >> Manifest ; \
	echo "Manifest : Manifest file" >> Manifest ; \
	for f in ${sort ${wildcard ${my_sources}}} ; do \
	    echo $$f :  `head -3 $$f | sed -ne 's/^#:[^:]*:[ ]*\(.*\)$$/\1/p' -` >> Manifest ; \
	done ; \
	echo 

