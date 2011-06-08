#!/usr/bin/python
#: gen-web-lkddb.py : generate the static pages for web-lkddb
#
#  Copyright (c) 2007,2008,2010,2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import sys
import optparse
import os
import os.path
import re
import string
import time

import lkddb
import lkddb.linux
import lkddb.tables


configs = {}



def assemble_config_data(tree):
    for t in tree.tables.itervalues():
	for key, row in t.crows.iteritems():
	   print t.name, ">>>", key, "---", row
	   confs = key[-2]
	   for conf in confs.split():
		if not conf in configs:
		    configs[conf] = {}
		if not t.name in configs[conf]:
		    configs[conf][t.name] = []
		configs[conf][t.name].append(row)


def generate_pages(templdir, webdir):
    f = open(os.path.join(templdir, "template-config.html"), "r")
    template_config = string.Template(f.read())
    f.close()
    for config in configs.iterkeys():
	print config ###
	d = {}
	d['general'] = "<p><b>MISSING 'general'</b></p>"
	d['hardware'] = "<p><b>MISSING 'hardware'</b></p>"
        d['lkddb'] = "<p><b>MISSING 'lkddb'</b></p>"
        d['sources'] = "<p><b>MISSING 'sources'</b></p>"
	d['year'] = "<b>MISSING 'year'</b>"
	f = open(os.path.join(webdir, config+".html"), "w")
	f.write(template_config.substitute(d))
	f.flush()
	f.clore()


def make(options, templdir, webdir):
    
    tree = lkddb.linux.linux_kernel(lkddb.TASK_CONSOLIDATE, None, [])
    lkddb.init(options)
    lkddb.log.phase("read consolidated file")
    tree.read_consolidate(options.consolidated)
    lkddb.log.phase("assemble page data")
    assemble_config_data(tree)
    lkddb.log.phase("assemble page data")
    generate_pages(templdir, webdir)
    lkddb.log.phase("END [gen-web-lkddb.py]")

#
# main
#

if __name__ == "__main__":
    
    usage = "Usage: %prog [options] template-dir output-dir"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, consolidated="lkddb-all.data")
    parser.add_option("-q", "--quiet",	dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    parser.add_option("-f", "--input" , dest="consolidated",
                      action="store",	type="string",
                      help="consolidated lkddb database FILE", metavar="FILE")
    parser.add_option("-l", "--log",	dest="log_filename",
                      action="store",	type="string",
                      help="FILE to put log messages (default to stderr)", metavar="FILE")
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error("missing mandatory arguments: template directory and output directory")
    templdir = os.path.normpath(args[0])
    webdir = os.path.normpath(args[1])
    if not os.path.isdir(templdir):
	parser.error("first argument should be a directory (containing templates)")
    if not os.path.isdir(webdir):
        parser.error("second argument should be a directory (to put generated files)")

    options.versioned = False
    options.year = time.strftime("%Y", time.gmtime())

    make(options, templdir, webdir)

