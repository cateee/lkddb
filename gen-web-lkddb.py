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
import lkddb.ids
import lkddb.tables


configs = {}
ids = {}




def assemble_config_data(storage):
    for tname, textra in storage.available_tables.iteritems():
	print "doing ", tname, textra[1].name, "in", textra[0]
	treename = textra[0]
	t = textra[1]
        if t.kind == ("linux-kernel", "device") or (
            t.kind == ("linux-kernel", "special") and t.name == "kconf"):
	    for key1, values1 in t.crows.iteritems():
	        for key2, values2 in values1.iteritems():
#	   	    print t.name, ">>>", key1, ">>", key2 , "---", values2
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
        elif t.kind == ("ids", "ids"):
	    ids[t.name] = {}
	    for key1, values1 in t.crows.iteritems():
		for key2, values2 in values1.iteritems():
#		    print t.name, ">>>", key1, ">>", key2 , "---", values2
		    ids[t.name][key1] = values2[0][0]


def generate_pages(templdir, webdir):
    f = open(os.path.join(templdir, "template-config.html"), "r")
    template_config = string.Template(f.read())
    f.close()
    for config_full, table in configs.iteritems():
	# print config_full ####
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

	#------
	# start of systems and sources

	systems = [] # -> system, [formated lines]
	sources = []
		
	#------
	# PCI
        if table.has_key('pci'):
            rows = table['pci']
	    sub_ids = ids.get('pci_ids', {})
	    sub_class_ids = ids.get('pci_class_ids', {})
	    lines = []
	    for key1, key2, values, versions in rows:
		vendor, device, subvendor, subdevice, class_mask = key1
		line = ""
                if vendor != "....":
                    line += "vendor: <code>" + vendor + "</code>"
		    name = sub_ids.get((vendor, "....", "....", "...."), None)
		    if name:
                         line += ' ("<i>' + escape(name) + '</i>")'
                    if device != "....":
                        line += ", device: <code>" + device + "</code>"
			name = sub_ids.get((vendor, device, "....", "...."), None)
			if name:
                            line += ' ("<i>' + escape(name) + '</i>")'
                        if subvendor != "...."  and  subdevice != "....":
                            line +=  ", subvendor: <code>" + subvendor + "</code>, subdevice: <code>" + subdevice + "</code>"
			    name = sub_ids.get((vendor, device, subvendor, subdevice), None)
			    if name:
                                line += ' ("<i>' + escape(name) + '</i>")'
		class_, subclass, prog_if = ( class_mask[0:2], class_mask[2:4], class_mask[4:6])
		if class_ != "..":
		    if line:
			line += ", "
                    line += "class: <code>" + class_ + "</code>"
		    name = sub_class_ids.get((class_, "..", ".."), None)
		    if name:
                        line += ' ("<i>' + escape(name) + '</i>")'
                    if subclass != "..":
                        line += ", subclass: <code>" + subclass + "</code>"
			name = sub_class_ids.get((class_, subclass, ".."), None)
			if name:
                            line += ' ("<i>' + escape(name) + '</i>")'
                        if prog_if != "..":
                            line += ", prog-if: <code>" + prog_if + "</code>"
			    name = sub_class_ids.get((class_, subclass, prog_if), None)
			    if name:
                                line += ' ("<i>' + escape(name) + '</i>")'
		if line:
		    lines.append(line)
	    if lines:
	        lines.sort()
	        systems.append(('PCI', '<p>Numeric ID (from LKDDb) and names (from pci.ids) of recognized devices:</p>', lines))
		sources.append('The <a href="http://pciids.sourceforge.net/">Linux PCI ID Repository</a>.')

        #------
        # USB
        if table.has_key('usb'):
            rows = table['usb']
            sub_ids = ids.get('usb_ids', {})
            sub_class_ids = ids.get('usb_class_ids', {})
            lines = []
            for key1, key2, values, versions in rows:
		vendor, product, dev_class, dev_subclass, dev_protocol, if_class, if_subclass, if_protocol = key1
                line = ""
                if vendor != "....":
                    line += "vendor: <code>" +  vendor + "</code>"
		    name = sub_ids.get((vendor, "...."), None)
		    if name:
                        line += ' ("<i>' + escape(name) + '</i>")'
                    if product != "....":
                        line += ", product: <code>" + product + "</code>"
			name = sub_ids.get((vendor, product), None)
			if name:
                             line += ' ("<i>' + escape(name) + '</i>")'
		# USB: device class
                if dev_class != "..":
                    if line != "":
                        line += ", "
                    line += "device class: <code>" + dev_class + "</code>"
		    name = sub_class_ids.get((dev_class, "..", ".."), None)
                    if name:
                         line += ' ("<i>' + escape(name) + '</i>")'
                    if dev_subclass != "..":
                        line += ", subclass: <code>" + dev_subclass + "</code>"
			name = sub_class_ids.get((dev_class, dev_subclass, ".."), None)
                        if name:
                            line += ' ("<i>' + escape(name) + '</i>")'
                        if dev_protocol != "..":
                            line +=  ", protocol: <code>" + dev_protocol + "</code>"
			    name = sub_class_ids.get((dev_class, dev_subclass, dev_protocol), None)
                            if name:
                                line += ' ("<i>' + escape(name) + '</i>")'

                # USB: interface class
                if if_class != "..":
                    if line != "":
                        line += ", "
                    line += "interface class: <code>" + if_class + "</code>"
                    name = sub_class_ids.get((if_class, "..", ".."), None)
                    if name:
                         line += ' ("<i>' + escape(name) + '</i>")'
                    if if_subclass != "..":
                        line += ", subclass: <code>" + if_subclass + "</code>"
                        name = sub_class_ids.get((if_class, if_subclass, ".."), None)
                        if name:
                            line += ' ("<i>' + escape(name) + '</i>")'
                        if if_protocol != "..":
                            line +=  ", protocol: <code>" + if_protocol + "</code>"
                            name = sub_class_ids.get((if_class, if_subclass, if_protocol), None)
                            if name:
                                line += ' ("<i>' + escape(name) + '</i>")'

                if line:
                    lines.append(line)
            if lines:
                lines.sort()
                systems.append(('USB', '<p>Numeric ID (from LKDDb) and names (from usb.ids) of recognized devices:</p>', lines))
                sources.append('The <a href="http://www.linux-usb.org/usb-ids.html">Linux USB ID Repository</a>.')


        #------
        # Assemble hardware and sources
	
	hardware = ""
	for title, descr, lines in systems:
	    hardware += ( '<h3>' + title + '</h3>\n' + descr + '\n<ul class="dblist">\n<li>' 
				+ "</li>\n<li>".join(lines)
				+ '</li>\n</ul>\n')

	if sources:
	    # Note: in template we set already few sources
	    pageitems['sources'] =  "</li>\n<li>".join(sources)
	else:
	    pageitems['sources'] = ""

     
	pageitems['hardware'] = hardware
        pageitems['lkddb'] = "<p><b>MISSING 'lkddb'</b></p>"
	pageitems['year'] = "<b>MISSING 'year'</b>"
	f = open(os.path.join(webdir, config+".html"), "w")
	f.write(template_config.substitute(pageitems))
	f.flush()
	f.close()

# some utility formating functions

escapemap = (
        ("&", "&amp;"),  # first item, not to replace e.g. the '&' in '&gt;'
        ("<", "&lt;"),
        (">", "&gt;"),
        ('"', "&quot;"),
        ("'", "&apos;"))

def escape(src):
    for c, esc in escapemap:
        src = src.replace(c, esc)
    return src



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
    vers = map(lambda v: v[2], versions)
    vers.sort()
    return ", ".join(vers)


def make(options, templdir, webdir):
    lkddb.init(options)

    storage = lkddb.storage()
    linux_kernel_tree = lkddb.linux.linux_kernel(lkddb.TASK_CONSOLIDATE, None, [])
    storage.register_tree(linux_kernel_tree)
    ids_files_tree = lkddb.ids.ids_files(lkddb.TASK_CONSOLIDATE, None)
    storage.register_tree(ids_files_tree)

    lkddb.log.phase("read consolidated file")
    storage.read_consolidate(options.consolidated)
    lkddb.log.phase("assemble config page data")
    assemble_config_data(storage)
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

