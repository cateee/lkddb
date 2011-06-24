
all: clean manifest lkddb merge web
.PHONY: lkddb chars merge web clean tar manifest

lkddb:
	time python ./build-lkddb.py -v -b lkddb -l log -k ~/kernel/linux-2.6/

# for debugging:
chars:
	time python ./build-lkddb.py -v -l log-char -b char -k ~/kernel/linux-2.6/ drivers/chars

merge:
	time python ./merge.py -v -l log-merge -o lkddb-all.data lkddb-[23].*.data

web:
	time python ./gen-web-lkddb.py -v -l log-web -f lkddb-all.data templates/ web-out/

clean:
	find . -name '*.pyc' -delete
	-rm -f Manifest

tar: clean manifest
	./utils.sh tar

manifest:
	echo Manifest : "Manifest file" > Manifest ; \
	for f in `find -name '*.py'` ; do \
	    echo $$f :  `head -3 $$f | sed -ne 's/^#:[^:]*:[ ]*\(.*\)$$/\1/p' -` >> Manifest ; \
	done

