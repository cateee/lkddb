#!/usr/bin/python
#: gen-web-lkddb.py : generate the static html pages for web-lkddb
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
	for key1, values1 in t.crows.iteritems():
	    for key2, values2 in values1.iteritems():
#	   	print t.name, ">>>", key1, ">>", key2 , "---", values2
		if t.kind == ("linux-kernel", "device") or (
		   t.kind == ("linux-kernel", "special") and t.name == "kconf"):
#		    if t.kind == ("linux-kernel", "special") and t.name == "kconf":
#			print t.name, key1, key2
	   	    for config in key2[0].split():
                        if not config.startswith("CONFIG_") or config == "CONFIG_":
                            lkddb.log.log("assemble_config_data: invalid CONFIG: %s in %s :: %s :: %s :: %s" %
                                                (config, t.name, key1, key2, values2))
			    continue
		        if not config in configs:
		            configs[config] = {}
		        if not t.name in configs[config]:
		            configs[config][t.name] = []
		        configs[config][t.name].append((key1, key2, values2[0], values2[1]))


def generate_pages(templdir, webdir):
    f = open(os.path.join(templdir, "template-config.html"), "r")
    template_config = string.Template(f.read())
    f.close()
    for config_full, table in configs.iteritems():
	print config_full ####
	config = config_full[7:]
	if config == "_UNKNOW__":
	    continue
	assert config[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789es"
	pageitems = {
	    'config': config,
	    'subindex': config[0].upper(),
	}
	
	#-------
	# kconf
	saved = {}
	favorite_prompt = None
	if table.has_key('kconf'):
	    rows = table['kconf']
	    if len(rows) > 1:
	        text = "<p>The Linux kernel configuration item <code>" +config_full+ "</code> has multiple definitions:\n"
	    else:
	        text = "<p>The Linux kernel configuration item <code>" +config_full+ "</code>:</p>\n<ul>" 
	    for key1, key2, values, versions in rows:
	        c, filename = key2
	        typ, descr, depends, helptext = values
	        descr = descr.strip()
	        if len(rows) > 1:
		    text += ("\n<h2><emph>" +descr+ "</emph> found in <code>" +filename+ "</code></h2>\n"+
			     "<p>The configuration item " +config_full+ ":</p>\n<ul>")
		    if filename.startswith("arch/x86/"):
		        favorite_prompt = descr
		    if saved.has_key(descr):
		        saved[descr] += 1
		    else:
		        saved[descr] = 1
	        else:
		    favorite_prompt = descr
	        text += (" <li>prompt: " +descr+ "</li>\n" +
                         " <li>type: "   +typ+ "</li>\n" +
                         " <li>depends on: <code>"   +prepare_depends(depends)+ "</code></li>\n" +
                         " <li>defined in " + url_filename(filename) + "</li>\n" +
                         " <li>found in Linux kernels: " +ver_str(versions)+ "</li>\n</ul>\n")
	        if len(rows) > 1:
		    text += "\n<h3>Help text</h3>\n<p>"
	        else:
		    text += "\n<h2>Help text</h2>\n<p>"
	        text += prepare_help(helptext) + "</p>\n"
	
	    pageitems['general'] = text + "\n"
	    if favorite_prompt:
	        pageitems['prompt'] = config_full+ ": " +favorite_prompt
	    else:
	        v = 0
	        for descr, vals in saved.iteritems():
	            if vals > v:
		        favorite_prompt = descr
		if favorite_prompt:
	            pageitems['prompt'] = config_full+ ": " +favorite_prompt
		else:
		    pageitems['prompt'] = config_full
	else:
	    pageitems['general'] = ("<p>The Linux kernel configuration item <code>" +config_full+ "</code>: \n"+
				    "<br />error: definition not found!</p>\n\n")
	    pageitems['prompt'] = config_full

	hardware = []
	sources = []
		
	#------
	# PCI
        if table.has_key('kconf'):
            rows = table['kconf']
	    for key1, key2, values, versions in rows:
		vendor, device, subvendor, subdevice, class_mask = key1
		
	

	pageitems['hardware'] = "<p><b>MISSING 'hardware'</b></p>"
        pageitems['lkddb'] = "<p><b>MISSING 'lkddb'</b></p>"
        pageitems['sources'] = "<p><b>MISSING 'sources'</b></p>"
	pageitems['year'] = "<b>MISSING 'year'</b>"
	f = open(os.path.join(webdir, config+".html"), "w")
	f.write(template_config.substitute(pageitems))
	f.flush()
	f.close()

# some utility formating functions

config_re = re.compile(r"CONFIG_([^_]\w*)")

help_local_re = re.compile(r"<file:([^>]*)>")
help_remote_re = re.compile(r"<(http:[^>]*)>")


def prepare_help(helptext):
    helptext = helptext.replace("&", "&amp;")
    helptext = config_re.sub(r'&&lt; a href="\1.html"&&gt;\1&&lt;/a&&gt;', helptext)
    helptext = help_local_re.sub(r'&&lt;a href="http://lxr.linux.no/linux/\1"&&gt;\1&&lt;/a&&gt;', helptext)
    helptext = help_remote_re.sub(r'&&lt;a href="\1"&&gt;\1&&lt;/a&&gt;', helptext)
    helptext = helptext.replace("<", "&lt;").replace(">", "&gt;")
    helptext = helptext.replace("&&lt;", "<").replace("&&gt;", ">")
    helptext = helptext.strip().replace("\n\n", "</p>\n\n<p>")
    return helptext

def url_config(config):
    return '<a href="' +config+ '.html">CONFIG_' +config+ '</a>'
def url_filename(filename):
    return  '<a href="http://lxr.linux.no/linux/' +filename+ '">' +filename+ '</a>'

def prepare_depends(depends):
    if not depends:
        return "(none)"
    ret = ""
    type = 0
    for c in depends:
        if c.isalnum() or c == "_":
            if type == 2:
                ret += " "
            type = 1
        elif c in frozenset("!=()&|"):
            if type == 1:
                ret += " "
            type = 2
        else:
            type = 0
        ret += c
    toks = ret.split()
    for i in range(len(toks)):
        if toks[i][0].isdigit()  or  toks[i][0].isalpha():
            toks[i] = '<a href="' +toks[i]+ '.html">CONFIG_' +toks[i]+ '</a>'
    return " ".join(toks).replace("&", "&amp;")

def str_kern_ver(ver):
    x = (ver >> 16) & 0xff
    y = (ver >> 8 ) & 0xff
    z =  ver        & 0xff
    return "%i.%i.%i" %(x,y,z)

def kernel_interval(min_ver, max_ver):
    if min_ver == -1:
        #print min_ver, max_ver
        #assert max_ver == -1
        return ("found only in <code>HEAD</code> (i.e. after release %s)" % str_kern_ver(db_max_ver), "HEAD")
    if db_min_ver == min_ver:
        ret = "before %s version" % str_kern_ver(db_min_ver)
        ret2 = ""
    else:
        ret = "from %s release" % str_kern_ver(min_ver)
        ret2 = "from release %s" % str_kern_ver(min_ver)
    if db_max_ver == max_ver:
        ret += " still available on %s release" % str_kern_ver(db_max_ver)
    else:
        ret += " to %s release, thus this is an <b>obsolete</b> configuration" % str_kern_ver(max_ver)
        if ret2:
            ret2 = "obsolete, available from %s until %s" % (str_kern_ver(min_ver), str_kern_ver(max_ver))
        else:
            ret2 = "obsolete, available until %s" % str_kern_ver(max_ver)
    return ret, ret2

def ver_str(versions):
    vers = list(versions)
    vers.sort()
    return ", ".join(vers)


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

