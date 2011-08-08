#!/usr/bin/python
#: gen-web-lkddb.py : generate the static html pages for web-lkddb
#
#  Copyright (c) 2007,2008,2010,2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import optparse
import os.path
import re
import string
import time

import lkddb
import lkddb.linux
import lkddb.ids
import lkddb.tables

tables = {}
configs = {}
ids = {}
config_pages = {}  # 'A' -> [ ('CONFIG_ATM', '2.6.25, 2.6.26'), ('CONFIG_ABC', ...]

def assemble_config_data(storage):
    for tname, textra in storage.available_tables.iteritems():
	treename = textra[0]
	t = textra[1]
	tables[tname] = t
        if t.kind == ("linux-kernel", "device") or (
            t.kind == ("linux-kernel", "special") and t.name == "kconf"):
	    for key1, values1 in t.crows.iteritems():
	        for key2, values2 in values1.iteritems():
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
		    ids[t.name][key1] = values2[0][0]


def generate_config_pages(templdir, webdir):
    f = open(os.path.join(templdir, "template-config.html"), "r")
    template_config = string.Template(f.read())
    f.close()
    year = time.strftime("%Y", time.gmtime())
    for config_full, table in configs.iteritems():
	config = config_full[7:]
	if config == "_UNKNOW__":
	    continue
	assert config[0] in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789es"
	subindex = config[0].upper()
        if subindex.isdigit():
            subindex = "0-9"
	pageitems = {
	    'config': config,
	    'subindex': subindex,
	    'year': year
	}

        #-------
        # module
	lines = []
	if table.has_key('module'):
            rows = table['module']
	    for key1, key2, values, versions in rows:
		lines.append('<code>' + key1[0] + '</code>')
	if lines:
	    lines.sort()
	    modules = "<li>modules built: " +", ".join(lines)+ "</li>\n"
	else:
	    modules = ""

	#-------
	# kconf
	saved = {}
	favorite_prompt = None
	all_versions = set([])
	if table.has_key('kconf'):
	    rows = table['kconf']
	    text2 = []
	    if len(rows) > 1:
	        text = "<p>The Linux kernel configuration item <code>" +config_full+ "</code> has multiple definitions:\n"
	    else:
	        text = "<p>The Linux kernel configuration item <code>" +config_full+ "</code>:</p>\n<ul>" 
	    for key1, key2, values, versions in rows:
		typ, descr = key1
	        c, filename = key2
	        depends, helptext = values
	        descr = descr.strip()
		txt = ""
	        if len(rows) > 1:
		    txt += ("\n<h2><emph>" +descr+ "</emph> found in <code>" +filename+ "</code></h2>\n"+
			     "<p>The configuration item " +config_full+ ":</p>\n<ul>")
		    if filename.startswith("arch/x86/"):
		        favorite_prompt = descr
		    if saved.has_key(descr):
		        saved[descr] += 1
		    else:
		        saved[descr] = 1
	        else:
		    favorite_prompt = descr
	        txt += ("<li>prompt: " +descr+ "</li>\n" +
                         "<li>type: "   +typ+ "</li>\n" +
                         "<li>depends on: <code>"   +prepare_depends(depends)+ "</code></li>\n" +
                         "<li>defined in " + url_filename(filename) + "</li>\n" +
                         "<li>found in Linux kernels: " +
                            ver_list_str(versions, compress=True)+ "</li>\n" +
			 modules + "</ul>\n")
                all_versions.update(versions)
	        if len(rows) > 1:
		    txt += "\n<h3>Help text</h3>\n<p>"
	        else:
		    txt += "\n<h2>Help text</h2>\n<p>"
                if not helptext:
                    helptext = "(none)"
	        text2.append(txt + prepare_help(helptext) + "</p>\n")
	
	    text2.sort()
	    pageitems['general'] = text + "".join(text2)
	    if favorite_prompt:
	        pageitems['title'] = config_full+ ": " + favorite_prompt
	    else:
	        v = 0
	        for descr, vals in saved.iteritems():
	            if vals > v:
		        favorite_prompt = descr
		if favorite_prompt:
	            pageitems['title'] = config_full+ ": " + favorite_prompt
		else:
		    pageitems['title'] = config_full
	else:
	    pageitems['general'] = ("<p>The Linux kernel configuration item <code>" +config_full+ "</code>: \n"+
				    "<br />error: definition not found!</p>\n\n")
	    pageitems['title'] = config_full

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
		vendor, product, dev_class, dev_subclass, dev_protocol, if_class, if_subclass, if_protocol, bcdlow, bcdhi = key1
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
		# USB: bcd
                if bcdlow != "0000" and bcdhi != "ffff":
                    if line != "":
                        line += ", "
                    line += "bcd min: " +bcdlow+ " (hex), bcd max:" +bcdhi + " (hex)"
		# USB end
                if line:
                    lines.append(line)
            if lines:
                lines.sort()
                systems.append(('USB', '<p>Numeric ID (from LKDDb) and names (from usb.ids) of recognized devices:</p>', lines))
                sources.append('The <a href="http://www.linux-usb.org/usb-ids.html">Linux USB ID Repository</a>.')

        #------
        # EISA
        if table.has_key('eisa'):
            rows = table['eisa']
            sub_ids = ids.get('eisa_ids', {})
            lines = []
            for key1, key2, values, versions in rows:
		line = ""
                sig = key1[0][1:-1]
                line += "signature: <code>" + sig + "</code>"
                name = sub_ids.get((sig,), None)
                if name:
                     line += ' ("<i>' + escape(name) + '</i>")'
                lines.append(line)
            if lines:
                lines.sort()
                systems.append(('EISA', '<p>Numeric ID (from LKDDb) and names (from eisa.ids) of recognized devices:</p>', lines))
                sources.append('The <a href="http://www.kernel.org/">Linux Kernel</a> (eisa.ids).')

        #------
        # ZORRO
        if table.has_key('zorro'):
            rows = table['zorro']
            sub_ids = ids.get('zorro_ids', {})
            lines = []
            for key1, key2, values, versions in rows:
                manufacter, product = key1
                line = ""
                if manufacter != "....":
                    line += "manufacter: <code>" + manufacter + "</code>"
                    name = sub_ids.get((manufacter, "...."), None)
                    if name:
                         line += ' ("<i>' + escape(name) + '</i>")'
                    if product != "....":
                        line += ", product: <code>" + product + "</code>"
                        name = sub_ids.get((manufacter, product), None)
                        if name:
                            line += ' ("<i>' + escape(name) + '</i>")'
                if line:
                    lines.append(line)
            if lines:
                lines.sort()
                systems.append(('ZORRO', '<p>Numeric ID (from LKDDb) and names (from zorro.ids) of recognized devices:</p>', lines))
                sources.append('The <a href="http://www.kernel.org/">Linux Kernel</a> (zorro.ids)')

        #------
        # Assemble hardware and sources
	
	hardware = ""
	for title, descr, lines in systems:
	    hardware += ( '<h3>' + title + '</h3>\n' + descr + '\n<ul class="dblist">\n<li>' 
				+ "</li>\n<li>".join(lines)
				+ '</li>\n</ul>\n')
	pageitems['hardware'] = hardware

        #------
        # lkddb
	
        lines = []
	for tname, t in table.iteritems():
	    if tname == "kconf":
		continue
	    line_templ = tables[tname].line_templ.rstrip()
            for key1, key2, values, versions in table[tname]:
		row = key1 + (url_config(key2[0]), url_filename(key2[1])) + values
		lines.append("lkddb " + line_templ % row)
	lines.sort()
	if not lines:
	    lines.append("(none)")
	lkddb = ( '<h3>LKDDb</h3>\n<p>Raw data from LKDDb:</p>\n<ul class="dblist">\n<li><code>'
                   + "</code></li>\n<li><code>".join(lines)
                   + '</code></li>\n</ul>\n')
	pageitems['lkddb'] = lkddb

	if sources:
	    # Note: in template we set already few sources
	    pageitems['sources'] = "<li>" + "</li>\n<li>".join(sources) + "</li>"
	else:
	    pageitems['sources'] = ""

        if not config_pages.has_key(subindex):
            config_pages[subindex] = []
        config_pages[subindex].append((config, all_versions))

	f = open(os.path.join(webdir, config+".html"), "w")
	f.write(template_config.substitute(pageitems))
	f.flush()
	f.close()


def generate_index_pages(templdir, webdir):
    f = open(os.path.join(templdir, "template-index.html"), "r")
    template_index = string.Template(f.read())
    f.close()
    year = time.strftime("%Y", time.gmtime())
    indices = config_pages.keys()
    indices.sort()
    count = {}
    for subindex, config in config_pages.iteritems():
	count[subindex] = len(config)
    for idx in indices + ["main"]:   # add also the main index page
	page = ""
	for idx2 in indices:
            if idx != idx2:
                page += ('<li><a href="index_' +idx2+ '.html">'
                          +idx2+ ' index</a> (with ' +str(count[idx2])+ ' configuration items)</li>\n')
            else:
                page += ('<li><b>' +idx2+ '</b> (with ' +str(count[idx2])+ ' configuration items)<ul>\n')
		pages_in_idx2 = config_pages[idx2]
		pages_in_idx2.sort()
                for conf, all_ver in pages_in_idx2:
                    if all_ver:
                        ver = ' (<small>' + ver_list_str(all_ver, compress=True) + '</small>)'
                    page += ('<li><a href="' +conf+ '.html">CONFIG_' +conf+ '</a>'+ver+'</li>\n')
                page += '</ul></li>\n'

        if idx == "main":
            key = idx
        else:
            key = "'" + idx + "'"
	pageitems = {
	    'year': year,
	    'page': page,
	    'key': key,
        }

	if idx == "main":
	    fn = os.path.join(webdir, "index.html")
	else:
	    fn = os.path.join(webdir, "index_" + idx + ".html")
        f = open(fn, "w")
        f.write(template_index.substitute(pageitems))
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
    helptext = config_re.sub(r'&&lt;a href="\1.html"&&gt;\1&&lt;/a&&gt;', helptext)
    helptext = help_local_re.sub(r'&&lt;a href="http://lxr.linux.no/source/\1"&&gt;\1&&lt;/a&&gt;', helptext)
    helptext = help_remote_re.sub(r'&&lt;a href="\1"&&gt;\1&&lt;/a&&gt;', helptext)
    helptext = helptext.replace("<", "&lt;").replace(">", "&gt;")
    helptext = helptext.replace("&&lt;", "<").replace("&&gt;", ">")
    helptext = helptext.strip().replace("\n\n", "</p>\n\n<p>")
    return helptext

def url_config(config):
    cc = config.split()
    cc.sort()
    ret = []
    for c in cc:
        ret.append('<a href="' +c[7:]+ '.html">' +c+ '</a>')
    return " ".join(ret)

def url_filename(filename):
    return  '<a href="http://lxr.linux.no/source/' +filename+ '">' +filename+ '</a>'

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
    v1 = (ver >> 16) & 0xff
    v2 = (ver >> 8 ) & 0xff
    v3 =  ver        & 0xff
    if v1 < 3 or v3 != 0:
        return "%i.%i.%i" %(v1, v2, v3)
    else:
        return "%i.%i" %(v1, v2)

def ver_list_str(versions, compress=False):
    versions = list(versions)
    versions.sort()
    # check if last string is a non-release version
    if versions[-1][3] < 0:
        name, ver, verstr, serie = versions[-1]
        basestr = str_kern_ver(ver[0])
        if ver[1] < 0:
            head = [basestr + "-rc+HEAD"]
        else:
            head = [basestr + "+HEAD"]
    else:
        head = []
    versions = filter(lambda v: v[3]>=0, versions)
    if not compress:
        ret = map(lambda v: v[2], versions)
        return ", ".join(ret + head)
    else:
        prev = (0,0,0)
        prev_str = "0.0.0"
        start = None
        start_str = None
        ret = []
        for name, ver, v_str, serie in versions + [('', (-1,-1,-1), "-1,-1,-1", -1)]:
            v = ((ver[0] >> 16) & 0xff, (ver[0] >> 8 ) & 0xff, ver[0] & 0xff)
            if ( (v[0] < 3  and v[0] == prev[0] and v[1] == prev[1] and v[2] == prev[2]+1) or
                 (v[0] >= 3 and v[0] == prev[0] and v[1] == prev[1]+1) ):
                if start == None:
                    # prev is the first of the current serie
                    start = prev
                    start_str = prev_str
            else:
                if start != None:
                    # start to prev are a serie
                    ret.append(start_str + "&ndash;" + prev_str)
                    start = None
                else:
                    ret.append(prev_str)
            prev = v
            prev_str = v_str
        return ", ".join(ret[1:] + head)


# compress=False
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1)
                    ]), False) == "2.6.5"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x020606,0,0), "2.6.6", 1)
                    ]), False) == "2.6.5, 2.6.6"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x020605,0,123), "2.6.5", -1)
                    ]), False) == "2.6.5, 2.6.5+HEAD"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x020606,-20,123), "2.6.3-rc12-2323", -1)
                    ]), False) == "2.6.5, 2.6.6-rc+HEAD"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x020606,0,0), "2.6.6", 1),
                         ("", (0x020606,0,2), "2.6.6+1234", -1),
                         ("", (0x020607,0,0), "2.6.7", 1),
                         ("", (0x020608,-10,0), "2.6.8-rc1", -1)
                    ]), False) == "2.6.5, 2.6.6, 2.6.7, 2.6.8-rc+HEAD"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x030000,0,0), "3.0", 1),
                         ("", (0x030001,0,0), "3.0.1", 1),
                         ("", (0x030200,0,234), "3.2", -1),
                    ]), False) == "2.6.5, 3.0, 3.0.1, 3.2+HEAD"

# compress=True
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1)
                    ]), True) == "2.6.5"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x020606,0,0), "2.6.6", 1)
                    ]), True) == "2.6.5&ndash;2.6.6"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x020607,0,0), "2.6.7", 1)
                    ]), True) == "2.6.5, 2.6.7"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x020606,0,0), "2.6.6", 1),
                         ("", (0x020607,0,0), "2.6.7", 1),
                         ("", (0x020611,0,0), "2.6.11", 1),
                    ]), True) == "2.6.5&ndash;2.6.7, 2.6.11"
assert ver_list_str(set([("", (0x020600,0,0), "2.6.0", 1),
                         ("", (0x020606,0,0), "2.6.6", 1),
                         ("", (0x020607,0,0), "2.6.7", 1),
                         ("", (0x020608,0,0), "2.6.8", 1),
                         ("", (0x020611,0,0), "2.6.11", 1),
                         ("", (0x030100,0,0), "3.1", 1),
                         ("", (0x030200,0,0), "3.2", 1),
                    ]), True) == "2.6.0, 2.6.6&ndash;2.6.8, 2.6.11, 3.1&ndash;3.2"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x030100,0,0), "3.1", 1),
                         ("", (0x030100,-20,200), "3.1-rc+HEAD", -11),
                    ]), True) == "2.6.5, 3.1"
assert ver_list_str(set([("", (0x020605,0,0), "2.6.5", 1),
                         ("", (0x030000,0,0), "3.0", 1),
                         ("", (0x030100,-20,200), "3.1-rc+HEAD", -11),
                    ]), True) == "2.6.5, 3.0, 3.1-rc+HEAD"



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
    generate_config_pages(templdir, webdir)
    generate_index_pages(templdir, webdir)
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

