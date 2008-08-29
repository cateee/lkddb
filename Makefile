# configuration #

kdir ?= ~/kernel/linux/
DESTDIR = ~/cateee.net

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

dist: lkddb.list dists/lkddb.list.gz dists/lkddb.list.bz2 ${tars}


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

webdistdep := lkddb.list dists/lkddb.list.gz dists/lkddb.list.bz2
webdistdep += ${dbs} ${ids} counts
webdistdep += dists/lkddb-sources-${DATE}.tar.gz dists/lkddb-${DATE}.tar.gz
webdistdep += dists/autokernconf-${DATE}.tar.gz

webdist: ${webdistdep}
	mkdir web-dist | /bin/true
	mkdir web-dist/lkddb-sources web-dist/lkddb web-dist/autokernconf  web-dist/ | /bin/true
	cp -p ${dbs} ${ids} counts  web-dist/lkddb
	cp -p dists/lkddb.list.gz dists/lkddb.list.bz2 web-dist/lkddb/
	cp -p dists/lkddb-sources-${DATE}.tar.gz web-dist/lkddb-sources/
	cp -p dists/lkddb-${DATE}.tar.gz web-dist/lkddb/
	cp -p dists/autokernconf-${DATE}.tar.gz web-dist/autokernconf/
	cp -rp web-lkddb/ web-dist/
	tar cf web-dist-${DATE}.tar web-dist
	gzip -9 web-dist-${DATE}.tar

webinst: webdist
	cp -pur web-dist/* $(DESTDIR)/sources/
	cp -pur web-lkddb/* $(DESTDIR)/lkddb/web-lkddb/

clean:
	rm -f count manifest *.pyc *.list lkddb.list.gz lkddb.list.bz2 counts config.auto

mrproper:
	rm -f *.ids

manifest:
	echo ${sources} > manifest

# lkddb

lkddb.list: ${lkddbgen}
	./build-lkddb.py ${kdir}

counts: lkddb.list
	@cat lkddb.list | grep -v '^#' | cut -f 2 | sort | uniq -c | sort -n > counts
	@echo >> counts
	@echo "TOTAL: `wc -l < lkddb.list`" >> counts

# other lists

pci.list: pci.ids
	./ids_to_list.py pci.ids pci.list "pci_ids"

usb.list: usb.ids
	./ids_to_list.py usb.ids usb.list "usb_ids"

eisa.list: eisa.ids
	cat eisa.ids | head -n 10 | grep '^#' > eisa.list
	cat eisa.ids | sed -ne 's/^\(.......\) \(.*\)$$/eisa\t\1\t\2/p' - >> eisa.list

zorro.list: zorro.ids
	./ids_to_list.py zorro.ids zorro.list "zorro_ids"


pci.ids:
	wget http://pci-ids.ucw.cz/pci.ids.bz2
	bzip2 -d pci.ids.bz2

usb.ids:
	wget http://www.linux-usb.org/usb.ids

eisa.ids:
	cp ${kdir}/drivers/eisa/eisa.ids .

zorro.ids:
	cp ${kdir}/drivers/zorro/zorro.ids .


web-lkddb/index.html: web-lkddb-gen.py lkddb.list pci.list usb.list eisa.list zorro.list
	[ -d web-lkddb ] || mkdir web-lkddb
	./web-lkddb-gen.py ${kdir} .
	
