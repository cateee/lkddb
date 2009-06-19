
all:
	python2.5 build-lkddb.py ~/kernel/linux-2.6/

clean:
	find . -name '*.pyc' -delete
	-rm Manifest

manifest:
	echo > Manifest ; \
	for f in `find -name '*.py'` ; do \
	    echo $$f  `head -3 $$f | grep '^#:' -` >> Manifest ; \
	done

