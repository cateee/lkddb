#!/usr/bin/python
#: web-lkddb-gen.py : prepare html pages from consolidated lkddb data
#
#  Copyright (c) 2007,2008,2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import sys
import os
import os.path
import re
import string
import time
import optparse
import sqlite3


escapemap = (
	("&", "&amp;"),  # first item, not to replace e.g. the '&' in '&gt;'
	("<", "&lt;"),
	(">", "&gt;"),
        ('"', "&quot;"),
        ("'": "&apos;"))

def escape(src):
    for c, esc in escapemap:
	src = src.replace(c, esc)
    return src


config_re = re.compile(r"CONFIG_([^_]\w*)")

help_local_re = re.compile(r"<file:([^>]*)>")
help_remote_re = re.compile(r"<(http:[^>]*)>")

def prepare_help(help):
    help = help.replace("&", "&amp;")
    help = help_local_re.sub(r'&&lt;a href="http://lxr.linux.no/source/\1"&&gt;\1&&lt;/a&&gt;', help)
    help = help_remote_re.sub(r'&&lt;a href="\1"&&gt;\1&&lt;/a&&gt;', help)
    help = help.replace("<", "&lt;").replace(">", "&gt;")
    help = help.replace("&&lt;", "<").replace("&&gt;", ">")
    return help
 
def url_config(conf):
    return '<a href="' + conf + '.html">CONFIG_' + conf + '</a>'
def url_filename(filename):
    return  '<a href="http://lxr.linux.no/source/'+filename+'">'+filename+'</a>'
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

def do_config_pages(templdir, webdir):
    index = {}
    f = open(os.path.join(templdir, "template-config.html"))
    config_template = string.Template(f.read())
    f.close()
    c = conn.cursor()
    types = {}
    for kkey_id, key in c.execute("SELECT kkey_id, key FROM kkeys;").fetchall():
	types[kkey_id] = key
    scanners = {}
    for scanner_id, name, db_attrs, format in c.execute(
		"SELECT scanner_id, name, db_attrs, format FROM scanners").fetchall():
	scanners[scanner_id] = (name, db_attrs, format)
    filename_ids = {}
    for filename_id, filename in c.execute(
            "SELECT filename_id, filename FROM filenames;").fetchall():
        filename_ids[filename_id] = filename
    config_ids = {}
    for config_id, config, min_ver, max_ver in c.execute(
	    "SELECT config_id, config, min_ver, max_ver FROM configs;").fetchall():
	config_ids[config_id] = (config.strip(), min_ver, max_ver)
    for config_id, config_ver in config_ids.iteritems():
        config, min_ver, max_ver = config_ver
	if config == "CONFIG__UNKNOW__":
	    continue
        if config == "CONFIG_":
	    continue ### log?
	conf = config[7:]
	indx = conf[0].upper()
	if not indx.isalpha():
	    indx = "0-9"
        out = {
            "conf": conf,
            "SubIndex": indx,
	    "subindex": indx.lower(),
	    "min_ver": min_ver,
	    "max_ver": max_ver,
            "year": year
        }
	ver_str, ver_str_short = kernel_interval(min_ver, max_ver)
	if index.has_key(indx):
	    index[indx].append((conf, ver_str_short))
	else:
	    index[indx] = [(conf,ver_str_short)]

# Kconfig items (type, prompt, help)
	kitems = c.execute("SELECT filename_id, kkey_type, descr, depends, help FROM kitems WHERE config_id=?;",
			(config_id,)).fetchall()
	if kitems:
	    if len(kitems) > 1:
		general = "<p>The Linux kernel configuration item <code>" + config + "</code> has multiple definitions:\n"
		for filename_id, kkey_type, descr, depends, help in kitems:
		    if not depends:
			depends = ""
		    filename = filename_ids[filename_id]
		    general += ( "<h2>" + filename + "</h2>\n<p>The configuration item " + config + ":</p>\n<ul>" +
		      "<li>prompt: " +descr+ "</li>\n" +
		      "<li>type: "   +types[kkey_id]+ "</li>\n" +
		      "<li>depends on: <code>"   +prepare_depends(depends)+ "</code></li>\n" +
		      "<li>defined in " + url_filename(filename) + "</li>\n" +
		      "<li>found in Linux Kernels: " +ver_str+ "</li>\n" +
		      "</ul>\n<h3>Help text</h3>\n<p>")
		    general += prepare_help(help) + "</p>\n"
	    else:
		filename_id, kkey_type, descr, depends, help = kitems[0]
		filename = filename_ids[filename_id]
		general = ( "<p>The Linux kernel configuration item <code>" + config + "</code>:</p>\n<ul>" +
                    "<li>prompt: " +descr+ "</li>\n" +
                    "<li>type: "   +types[kkey_id]+ "</li>\n" +
		    "<li>depends on: <code>"   +prepare_depends(depends)+ "</code></li>\n" +
                    "<li>defined in " + url_filename(filename) + "</li>\n" +
		    "<li>found in Linux Kernels: " +ver_str+ "</li>\n" +
                    "</ul>\n<h2>Help text</h2>\n<p>")
                general += prepare_help(help)  + "</p>\n"

            out["general"] = general.strip().replace("\n\n", "</p>\n\n<p>")
	else:
	    out["general"] = "unknow"
	    descr = "unknow"
	    print "config with no menu", config
	out["prompt"] = descr   # last item as default
	
# scan line (hardware and sources)
	lkddb_lines, pci_lines, usb_lines, eisa_lines, zorro_lines, module_lines = ([], [], [], [], [], [])
	hardware = ""
	sources = ""
	for line_id, scanner_id, id, filename_id, min_ver, max_ver, line_txt in c.execute(
	    "SELECT line_id, scanner_id, id, filename_id,min_ver, max_ver, line FROM lines " +
	    " WHERE dep_id IN (SELECT dep_id FROM deps WHERE config_id=?);",
		(config_id,)).fetchall():
	    name, db_attrs, format = scanners[scanner_id]

# raw lkddb lines
            line = c.execute("SELECT " + db_attrs + " FROM " + name + "s WHERE " + name + "_id=?;",
                    (id,)).fetchone()

	    if line_txt:
                fields = line_txt.split("\t:: ")
                fields[1] = config_re.sub(r'<a href="\1.html">CONFIG_\1</a>', fields[1])
                fields[2] = '<a href="http://lxr.linux.no/source/'+fields[2]+'">'+fields[2]+'</a>'
                lkddb_lines.append("<li><code>" + " :: ".join(fields) + "</code></li>\n")

# PCI
	    if name == "pci":
		v0, v1, v2, v3, v4 = line
		ss = ""
		if v0 != "....":
		    v0 = int(v0, 0x10)
		    ss += "vendor: <code>" + "%04x"%v0 + "</code>"
		    row = c.execute(
"SELECT name FROM pci_ids WHERE vendor=? AND device=-1 AND subvendor=-1;",
			("%i"%v0,)).fetchone()
		    if row:
			 ss += ' ("<i>' + escape(row[0]) + '</i>")'
                    if v1 != "....":
			v1 = int(v1, 0x10)
                        ss += ", device: <code>" + "%04x"%v1 + "</code>"
                        row = c.execute(
"SELECT name FROM pci_ids WHERE vendor=? AND device=? AND subvendor=-1;",
                            ("%i"%v0, "%i"%v1)).fetchone()
                        if row:
                             ss += ' ("<i>' + escape(row[0]) + '</i>")'
                        if  v2 != "...."  and  v3 != "....":
			    v2 = int(v2, 0x10)
			    v3 = int(v3, 0x10)
                            ss +=  ", subvendor, subdedvice: <code>" + "%04x"%v2 + "</code>, <code>" + "%04x"%v3 + "</code>"
                            row = c.execute(
"SELECT name FROM pci_ids WHERE vendor=? AND device=? AND subvendor=?;",
                                ("%i"%v0, "%i"%v1, "%i"%(v2*0x10000+v3))).fetchone()
                            if row:
                                 ss += ' ("<i>' + escape(row[0]) + '</i>")'
# PCI: class
		    v0, v1, v2 = ( v4[0:2], v4[2:4], v4[4:6])
                    if v0[0] != ".":
			v0 = int(v0, 0x10)
                        if ss != "":
                            ss += ", "
                        ss += "class: <code>" + "%02x"%v0 + "</code>"
                        row = c.execute(
"SELECT name FROM pci_class_ids WHERE class=? AND subclass=-1 AND prog_if=-1;",
                           ("%i"%v0,)).fetchone()
			if row:
			    ss += ' ("<i>' + escape(row[0]) + '</i>")'
                        if v1 != "..":
			    v1 = int(v1, 0x10)
                            ss += ", subclass: <code>" + "%02x"%v1 + "</code>"
                            row = c.execute(
"SELECT name FROM pci_class_ids WHERE class=? AND subclass=? AND prog_if=-1;",
                               ("%i"%v0, "%i"%v1)).fetchone()
                            if row:
                                ss += ' ("<i>' + escape(row[0]) + '</i>")'
                            if v2 != "..":
				v2 = int(v2, 0x10)
                                ss += ", prog-if: <code>" + "%02x"%v2 + "</code>"
                                row = c.execute(
"SELECT name FROM pci_class_ids WHERE class=? AND subclass=? AND prog_if=?;",
                                   ("%i"%v0, "%i"%v1, "%i"%v2)).fetchone()
                                if row:
                                    ss += ' ("<i>' + escape(row[0]) + '</i>")'
		if ss:
		    pci_lines.append(ss)
#                    if ss:
#                cic = []
#                for i in lkddb_inverse['pci'].get(pci, []):
#                    if i == conf:
#                        continue
#                    cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
#                if cc:
#                    ss += "; (also in " + ", ".join(cc) + ")"
#                s += "<li>" + ss + "</li>\n"

# USB
            if name == "usb":
                v0, v1, v2, v3, v4, v5, v6, v7, v8, v9 = line
                ss = ""
                if v0 != "....":
                    v0 = int(v0, 0x10)
                    ss += "vendor: <code>" +  "%04x"%v0 + "</code>"
                    row = c.execute(
"SELECT name FROM usb_ids WHERE vendor=? AND device=-1;",
                        ("%i"%v0,)).fetchone()
                    if row:
                         ss += ' ("<i>' + escape(row[0]) + '</i>")'
                    if v1 != "....":
                        v1 = int(v1, 0x10)
                        ss += ", product: <code>" + "%04x"%v1 + "</code>"
                        row = c.execute(
"SELECT name FROM usb_ids WHERE vendor=? AND device=?;",
                            ("%i"%v0, "%i"%v1)).fetchone()
                        if row:
                             ss += ' ("<i>' + escape(row[0]) + '</i>")'
# USB: class
		v0, v1, v2 = ( v2, v3, v4)
                if v0 != "..":
                    if ss != "":
                        ss += ", "
                    v0 = int(v0, 0x10)
                    ss += "device class: <code>" + "%02x"%v0 + "</code>"
                    row = c.execute(
"SELECT name FROM usb_class_ids WHERE class=? AND subclass=-1 AND protocol=-1;",
                        ("%i"%v0,)).fetchone()
                    if row:
                         ss += ' ("<i>' + escape(row[0]) + '</i>")'
                    if v1 != "..":
                        v1 = int(v1, 0x10)
                        ss += ", subclass: <code>" + "%02x"%v1 + "</code>"
                        row = c.execute(
"SELECT name FROM usb_class_ids WHERE class=? AND subclass=? AND protocol=-1;",
                            ("%i"%v0, "%i"%v1)).fetchone()
                        if row:
                             ss += ' ("<i>' + escape(row[0]) + '</i>")'
                        if  v2 != "..":
                            v2 = int(v2, 0x10)
                            ss +=  ", protocol: <code>" + "%02x"%v2 + "</code>"
                            row = c.execute(
"SELECT name FROM usb_class_ids WHERE class=? AND subclass=? AND protocol=?;",
                                ("%i"%v0, "%i"%v1, "%i"%v2)).fetchone()
                            if row:
                                 ss += ' ("<i>' + escape(row[0]) + '</i>")'
# USB: interface class
                v0, v1, v2 = ( v5, v6, v7)
                if v0 != "..":
                    if ss != "":
                        ss += ", "
                    v0 = int(v0, 0x10)
                    ss += "interface class: <code>" + "%02x"%v0 + "</code>"
                    row = c.execute(
"SELECT name FROM usb_class_ids WHERE class=? AND subclass=-1 AND protocol=-1;",
                        ("%i"%v0,)).fetchone()
                    if row:
                         ss += ' ("<i>' + escape(row[0]) + '</i>")'
                    if v1 != "..":
                        v1 = int(v1, 0x10)
                        ss += ", subclass: <code>" + "%02x"%v1 + "</code>"
                        row = c.execute(
"SELECT name FROM usb_class_ids WHERE class=? AND subclass=? AND protocol=-1;",
                            ("%i"%v0, "%i"%v1)).fetchone()
                        if row:
                             ss += ' ("<i>' + escape(row[0]) + '</i>")'
                        if  v2 != "..":
                            v2 = int(v2, 0x10)
                            ss +=  ", protocol: <code>" + "%02x"%v2 + "</code>"
                            row = c.execute(
"SELECT name FROM usb_class_ids WHERE class=? AND subclass=? AND protocol=?;",
                                ("%i"%v0, "%i"%v1, "%i"%v2)).fetchone()
                            if row:
                                 ss += ' ("<i>' + escape(row[0]) + '</i>")'
# USB: bcd
		if v8 != "0000"  and  v9 != "ffff":
                    if ss != "":
                        ss += ", "
		    v8 = int(v8, 0x10)
		    v9 = int(v9, 0x10)
		    ss += "bcd min: "+"%i"% v8+", bcd max:"+"%i"% v9
                if ss:
                    usb_lines.append(ss)
#                    if ss:
#                cic = []
#                for i in lkddb_inverse['pci'].get(pci, []):
#                    if i == conf:
#                        continue
#                    cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
#                if cc:
#                    ss += "; (also in " + ", ".join(cc) + ")"
#                s += "<li>" + ss + "</li>\n"


# EISA
            if name == "eisa":
                v0 = line[0]
                ss = ""
                if v0 != "....":
                    ss += "signature: <code>" + escape(v0) + "</code>"
                    row = c.execute(
"SELECT name FROM eisa_ids WHERE id=?;",
                        (v0,)).fetchone()
                    if row:
                         ss += ' ("<i>' + escape(row[0]) + '</i>")'

                if ss:
                    eisa_lines.append(ss)
#                    if ss:
#                cic = []
#                for i in lkddb_inverse['pci'].get(pci, []):
#                    if i == conf:
#                        continue
#                    cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
#                if cc:
#                    ss += "; (also in " + ", ".join(cc) + ")"
#                s += "<li>" + ss + "</li>\n"

# Zorro
            if name == "zorro":
                v0, v1 = line
                ss = ""
                if v0 != "....":
                    v0 = int(v0, 0x10)
                    ss += "manufacter: <code>" + "%04x"%v0 + "</code>"
		    try:
                        row = c.execute(
"SELECT name FROM zorro_ids WHERE manufacturer=? AND product=-1;",
                            (v0,)).fetchone()
		    except sqlite3.OperationalError:
			print "zorro: invalid UTF8 in ", config, ", ignoring"
			row = None
                    if row:
                         ss += ' ("<i>' + escape(row[0]) + '</i>")'
                    if v1 != "....":
                        v1 = int(v1, 0x10)
                        ss += ", product: <code>" + "%04x"%v1 + "</code>"
                        row = c.execute(
"SELECT name FROM zorro_ids WHERE manufacturer=? AND product=?;",
                            (v0, v1)).fetchone()
                        if row:
                             ss += ' ("<i>' + escape(row[0]) + '</i>")'
                if ss:
                    zorro_lines.append(ss)
#                    if ss:
#                cic = []
#                for i in lkddb_inverse['pci'].get(pci, []):
#                    if i == conf:
#                        continue
#                    cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
#                if cc:
#                    ss += "; (also in " + ", ".join(cc) + ")"
#                s += "<li>" + ss + "</li>\n"

# modules
            if name == "module":
		v0, v1 = line
		module_lines.append("<code>" +v0+ "</code>")


	if lkddb_lines:
	    lkddb_lines.sort()
	    out["lkddb"] = "".join(lkddb_lines)
	else:
	    out["lkddb"] = "<li>(none)</li>\n"
        if pci_lines:
	    pci_lines.sort()
            hardware += ('<h3>PCI</h3>\n<p>Numeric ID (from LKDDb) and names (from pci.ids) of recognized devices:</p>\n<ul class="dblist">\n<li>' + "</li>\n<li>".join(pci_lines) + '</li>\n</ul>\n\n')
            sources += '<li>The <a href="http://pciids.sourceforge.net/">Linux PCI ID Repository</a> (pci.ids)</li>\n'
        if usb_lines:
	    usb_lines.sort()
            hardware += ('<h3>USB</h3>\n<p>Numeric ID (from LKDDb) and names (from usb.ids) of recognized devices:</p>\n<ul class="dblist">\n<li>' + "</li>\n<li>".join(usb_lines) + '</li>\n</ul>\n\n')
            sources += '<li>The <a href="http://www.linux-usb.org/">Linux-USB.org</a> (usb.ids)</li>\n'
        if eisa_lines:
	    eisa_lines.sort()
            hardware += ('<h3>EISA</h3>\n<p>Numeric ID (from LKDDb) and names (from eisa.ids) of recognized devices:</p>\n<ul class="dblist">\n<li>' + "</li>\n<li>".join(eisa_lines) + '</li>\n</ul>\n\n')
            sources += '<li>The <a href="http://www.kernel.org/">Linux Kernel</a> (eisa.ids)</li>\n'
        if zorro_lines:
	    zorro_lines.sort()
            hardware += ('<h3>ZORRO</h3>\n<p>Numeric ID (from LKDDb) and names (from zorro.ids) of recognized devices:</p>\n<ul class="dblist">\n<li>' + "</li>\n<li>".join(zorro_lines) + '</li>\n</ul>\n\n')
            sources += '<li>The <a href="http://www.kernel.org/">Linux Kernel</a> (zorro.ids)</li>\n'
	if module_lines:
	    out["general"] = out["general"].replace("</ul>", "<li>module created: " +", ".join(module_lines)+ "</li>\n</ul>")

# write it
#        out["others"] = others
        out["hardware"] = hardware
        out["sources"] = sources

        fn = os.path.join(webdir, conf+".html")
        f = open(fn, "wb")
	f.write(config_template.substitute(out).encode("utf_8"))
        f.close()

    do_index_pages(templdir, webdir, index)



def do_index_pages(templdir, webdir, index):
    f = open(os.path.join(templdir, "template-index.html"))
    index_template = string.Template(f.read())
    f.close()
    order = index.keys()
    order.sort()
    for idx in order + [""]:
	page = ""
	for idx2 in order:
	    if idx != idx2:
		page += ('<li><a href="index_' +idx2+ '.html">'
			  +idx2+ ' index</a> (with ' +str(len(index[idx2]))+ ' items)</li>\n')
	    else:
		page += ('<li><b>' +idx2+ '</b>(with ' +str(len(index[idx2]))+ ' items)<ul>\n')
		for conf, ver_str in index[idx2]:
		    if ver_str:
			ver_str = ' (' + ver_str + ')'
		    page += ('<li><a href="' +conf+ '.html"> CONFIG_'
                          +conf+ '</a>'+ver_str+'</li>\n')
		page += '</ul></li>\n'
	dict = {'key': idx,  'page': page,  'year': year}
	if idx != "":
            fn = os.path.join(webdir, 'index_' +idx.lower()+ '.html')
	else:
	    fn = os.path.join(webdir, 'index.html')
        f = open(fn, "wb")
        f.write(index_template.substitute(dict).encode("utf_8"))
        f.close()


def main():
    global options, templdir, webdir, year, conn, db_min_ver, db_max_ver
    usage = "usage: %prog [options] templ-dir web-dir"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=True, dbfile="lkddb.db")
    parser.add_option("-q", "--quiet", dest="verbose",
                    action="store_false",
                    help="don't print warning messages")
    parser.add_option("-o", "--output", dest="output",
                    action="store", type="string",
                    help="write warnings to FILE", metavar="FILE")
    parser.add_option("-f", "--dbfile", dest="dbfile",
                    action="store",     type="string",
                    help="path to sqlite database", metavar="FILE")
 
    (options, args) = parser.parse_args()
    if options.output and options.output != "-":
        logfile = open(options.output, "w")
    else:
        logfile = sys.stdout
    if len(args) < 2:
        parser.error("incorrect number of arguments")
    templdir = os.path.normpath(args[0])
    webdir = os.path.normpath(args[1])
    if not os.path.isdir(webdir):
        print "the second argument is not a directory: ", dir
        sys.exit(1)
    year = time.strftime("%Y", time.gmtime())
    conn = sqlite3.connect(options.dbfile)
    c = conn.cursor()
    row = c.execute("SELECT min_ver, max_ver, head_tag FROM version WHERE type = 1;").fetchone()
    if row:
	db_min_ver, db_max_ver, head_tag = row
    else:
	db_min_ver, db_max_ver, head_tag = (-1, -1, "(unknow)")

    do_config_pages(templdir, webdir)


if __name__ == "__main__":
    main()

