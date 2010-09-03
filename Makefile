
all: build-lkddb

build-lkddb:
	time python ./build-lkddb.py -v -b lkddb -l log  -k ~/kernel/linux-2.6/

# for debugging:
chars:
	time python ./build-lkddb.py -v -l log  -k ~/kernel/linux-2.6/ drivers/chars

consolidate:
	time python ./consolidate.py -v -l consolidate.log -o lkddb-all.data lkddb-2.6.*.data

clean:
	find . -name '*.pyc' -delete
	-rm -f Manifest

tar: clean
	./utils.sh tar

manifest:
	echo Manifest > Manifest ; \
	for f in `find -name '*.py'` ; do \
	    echo $$f  `head -3 $$f | grep '^#:' -` >> Manifest ; \
	done

