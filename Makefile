
all:
	time python build-lkddb.py -v -b lkddb -l log  -k ~/kernel/linux-2.6/

chars:
	time python build-lkddb.py -v -l log  -k ~/kernel/linux-2.6/ drivers/chars

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

