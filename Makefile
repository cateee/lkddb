#!/usr/bin/make -f
#: Makefile : rules to make, distribute and test lkddb
#
#  Copyright (c) 2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details


# --- configuration ---

# Note these option could be given in command line: e.g.:

#  $ make all kdir=/pub/linux-3.0/linux-3.0.0

# kernel directory
kdir ?= ~/kernel/linux/
DATA ?= data

# --- generic rules ---

all: Manifest lkddb web-out/index.html
.PHONY: lkddb merge web check-ids check-pci.ids check-usb.ids check-eisa.ids check-zorro.ids clean tests tar Manifest


# --- generic definitions ---

datafiles ?= $(shell bash -O nullglob -c "echo ${DATA}/lkddb-2.5.??.data ${DATA}/lkddb-2.6.?.data ${DATA}/lkddb-2.6.??.data ${DATA}/lkddb-3.?.data ${DATA}/lkddb-3.??.data ${DATA}/lkddb-4.?.data ${DATA}/lkddb-4.??.data ${DATA}/lkddb-5.?.data ${DATA}/lkddb-5.??.data")
my_sources = *.py lkddb/*.py lkddb/*/*.py templates/*.html utils/*.py utils/*.sh Makefile tests/*.py TODO lkddb/DESIGN .gitignore
all_sources = ${my_sources} GPL-2 GPL-3

# --- information and debug targers ---

listdata:
	@echo ${datafiles}

# --- clean targets ---

clean:
	-find . -name '*.pyc' -o -name '__pycache__' -delete
	-rm -f Manifest *.ids *.ids.bz2 *.list *.data *.log *.tmp
	-rm -f web-out/*.html

mrproper: clean
	-rm -f web-out/*
	-rm -Rf dist dist.old changes data*

# --- building lists ---

lkddb:
	time python3 ./build-lkddb.py -v -b ${DATA}/lkddb -l ${DATA}/lkddb-%.log -k ${kdir}

merge: ${DATA}/lkddb-all.data
${DATA}/lkddb-all.data: ${DATA}/ids.data ${datafiles} merge.py
	@[ -d ${DATA} ] || mkdir ${DATA}
	time python3 ./merge.py -v -l ${DATA}/merge.log -o ${DATA}/lkddb-all.data ${datafiles} ${DATA}/ids.data

web: ${DATA}/web-out/index.html
${DATA}/web-out/index.html: ${DATA}/lkddb-all.data templates/*.html gen-web-lkddb.py
	@[ -d ${DATA}/web-out ] || mkdir -p ${DATA}/web-out
	time python3 ./gen-web-lkddb.py -v -l ${DATA}/web.log -f ${DATA}/lkddb-all.data templates/ ${DATA}/web-out/


# These targets require extern files
# We download files only with explicit user agreement (e.g. "make check-ids")

check-pci.ids:
	(cd ${DATA} && wget -N https://pci-ids.ucw.cz/v2.2/pci.ids.bz2 && bzip2 -kfd pci.ids.bz2)
check-usb.ids:
	(cd ${DATA} && wget -N http://www.linux-usb.org/usb.ids.bz2 && bzip2 -kfd usb.ids.bz2 )
check-eisa.ids: ${kdir}/drivers/eisa/eisa.ids
	cp ${kdir}/drivers/eisa/eisa.ids ${DATA}/
check-zorro.ids: ${kdir}/drivers/zorro/zorro.ids
	cp ${kdir}/drivers/zorro/zorro.ids ${DATA}/
check-ids: check-pci.ids check-usb.ids check-eisa.ids check-zorro.ids

${DATA}/ids.data: ${DATA}/pci.ids ${DATA}/usb.ids ${DATA}/eisa.ids ${DATA}/zorro.ids
	@if ! [ -f ${DATA}/pci.ids -a -f ${DATA}/usb.ids -a -f ${DATA}/eisa.ids -a -f ${DATA}/zorro.ids ] ; then \
	    echo "Missing one ids file."; echo "Run 'make check-ids' to download the needed files"; exit 1; \
	fi
	time python3 ./ids_importer.py -v -b ${DATA}/ids -l ${DATA}/ids.log ${DATA}/pci.ids ${DATA}/usb.ids ${DATA}/eisa.ids ${DATA}/zorro.ids


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

