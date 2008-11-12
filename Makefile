# configuration #

kdir ?= ~/kernel/linux/

DESTDIR = ~/cateee.net
DESTSRC = ${DESTDIR}/sources
DESTWEB = ${DESTDIR}/lkddb

# end of configuration #


DATE = $(shell date --rfc-3339=date)

dbs = lkddb.list pci.list usb.list eisa.list zorro.list
ids = pci.ids usb.ids eisa.ids zorro.ids

sources = Makefile

# lkddb-generator
lkddbgen := build-lkddb.py devicetables.py kbuildparser.py srcparser.py utils.py
sources += ${lkddbgen}

# lkddb
sources += ids_to_list.py

# autokernconf
autokernconf := kdetect.sh autokernconf.sh
sources += ${autokernconf}

# web generator
sources += web-lkddb-gen.py


tars := dists/lkddb-sources-${DATE}.tar.gz dists/lkddb-${DATE}.tar.gz dists/autokernconf-${DATE}.tar.gz

all: lkddb.list counts web-lkddb/index.html

dist: dists/lkddb.list.gz dists/lkddb.list.bz2 ${tars} ${dbs} ${ids} counts
	cp -p ${dbs} ${ids} counts                     ${DESTSRC}/lkddb/
	cp -p dists/lkddb.list.gz dists/lkddb.list.bz2 ${DESTSRC}/lkddb/
	cp -p dists/lkddb-${DATE}.tar.gz               ${DESTSRC}/lkddb
	cp -p dists/lkddb-sources-${DATE}.tar.gz       ${DESTSRC}/lkddb-sources/
	cp -p dists/autokernconf-${DATE}.tar.gz        ${DESTSRC}/autokernconf/
	cp -rp web-lkddb/			       ${DESTWEB}/
	

ids: $(ids)
	python ids_to_list.py

dists/lkddb-sources-${DATE}.tar.gz: ${sources}
	rm -Rf dists/lkddb-sources-${DATE}*
	mkdir dists/lkddb-sources-${DATE}
	cp -p ${sources} dists/lkddb-sources-${DATE}
	( cd dists ; tar cf lkddb-sources-${DATE}.tar lkddb-sources-${DATE} )
	gzip -9 dists/lkddb-sources-${DATE}.tar

dists/lkddb-${DATE}.tar.gz: ${dbs}
	rm -Rf dists/lkddb-${DATE}*
	mkdir dists/lkddb-${DATE}
	cp -p ${dbs} dists/lkddb-${DATE}
	( cd dists ; tar cf lkddb-${DATE}.tar lkddb-${DATE} )
	gzip -9 dists/lkddb-${DATE}.tar

dists/autokernconf-${DATE}.tar.gz: ${autokernconf}
	rm -Rf dists/autokernconf-${DATE}*
	mkdir dists/autokernconf-${DATE}
	cp -p ${autokernconf} dists/autokernconf-${DATE}
	( cd dists ; tar cf autokernconf-${DATE}.tar autokernconf-${DATE} )
	gzip -9 dists/autokernconf-${DATE}.tar

dists/lkddb.list.gz: lkddb.list
	gzip -9 -c lkddb.list > dists/lkddb.list.gz

dists/lkddb.list.bz2: lkddb.list
	bzip2 -9 -c lkddb.list > dists/lkddb.list.bz2


clean:
	rm -f manifest lkddb.db *.pyc *.list lkddb.list.gz lkddb.list.bz2 counts config.auto

mrproper:
	rm -f *.ids

manifest:
	echo ${sources} > manifest


# lkddb

lkddb.list: ${lkddbgen}
	python build-lkddb.py -l lkddb.list ${kdir}

counts: Makefile lkddb.list
	@cat lkddb.list | grep -v '^#' | cut -f 2 | sort | uniq -c | sort -n > counts
	@echo >> counts
	@echo "TOTAL: `wc -l < lkddb.list`" >> counts


# web

web-lkddb/index.html: web-lkddb-gen.py lkddb.list pci.list usb.list eisa.list zorro.list
	rm -Rf web-lkddb ;  mkdir web-lkddb
	python web-lkddb-gen.py . web-lkddb


# other lists

pci.list: pci.ids ids_to_list.py
	python ids_to_list.py pci
usb.list: usb.ids ids_to_list.py
	python ids_to_list.py usb
eisa.list: eisa.ids ids_to_list.py
	python ids_to_list.py eisa
zorro.list: zorro.ids ids_to_list.py
	python ids_to_list.py zorro
pci.ids:
	wget http://pciids.sourceforge.net/v2.2/pci.ids.bz2
	bzip2 -d pci.ids.bz2
usb.ids:
	wget http://www.linux-usb.org/usb.ids
eisa.ids:
	cp ${kdir}/drivers/eisa/eisa.ids .
zorro.ids:
	cp ${kdir}/drivers/zorro/zorro.ids .

