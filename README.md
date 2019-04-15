# About LKDDb

LKDDb is an attempt to build a comprehensive database of hardware and
protocols know by Linux kernels.

The driver database includes numeric identifiers of hardware
(e.g. PCI vendor and PCI device numbers),
the kernel configuration option required to build the driver,
the driver filename itself, and the kernel versions which support
such hardware.

The database is build automagically from kernel sources, so it is
very easy to have always the database updated.

There are two outputs: a text based database, to be processed
automatically (see `lkddb.list`),
and the [web LKDdb](https://cateee.net/lkddb/web-lkddb/) version,
which includes also text and hardware strings from kernel and other
sources.

*See also [History.md](History.md)*

## Autoconfiguration

Originally LKDDb were a tools for an other tools: an autoconfiguration
tool for Linux Kernel, either standalone or integrated in CML2.

I will put (later this year) a sister project with such scripts.
It is not really maintained, but scripts works, and just the database
need to be updated regularly.

# Use

The simple use:

    python3 ./build-lkddb.py -b kddb -l lkddb.log ~/kernel/linux
    
The last arguments is the directory of source kernel.
It is convenient to have a pristine source (without modifications
and binary files from compilation).
Users must get the source (e.g. from https://kernel.org)

The file `utils/update.sh` contains a script I run in a cronjob,
which take care to update the git repository, getting the
relavant pci.ids and ubs.ids lists from internet, build the
lkddb database for the newest kernel, merge results and build
the website.  So this file is the file you need to look for the
entire workflow.

## About the web site

I put in `template` the two simple templates I use to build the
default web interfaces, they are not so good (and they contain
my google id).

The site is created on update, so just static files, which are easy
to deploy, fast (no load problems), and no need of database (so
really fast).

Additionally, the deployed website is compared to the new generated
one, and only changes are sent to the web servers.
So generation time of pages could be used to further cache files
(and good web bot, e.g. of web engines, will not download again
the page if they find it is the same as the last one.)
