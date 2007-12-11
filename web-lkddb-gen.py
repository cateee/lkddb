#!/usr/bin/python
#: build-lkddb.py : hardware database generator from kernel sources
#
#  Copyright (c) 2007  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import sys, os, os.path, re, string, time, optparse

db_dir = "."

page = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
   "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <link href="http://cateee.net/template/lkddb.css" rel="stylesheet" type="text/css" />
  <link rel="icon" type="image/png" href="http://cateee.net/cateee.png">
  <title>Linux Kernel Driver Database: CONFIG_$conf: $prompt</title>
</head>

<body xml:lang="en" lang="en">

<div class="hnav">
<p>
  Navigation:
  <a href="http://cateee.net/lkddb/">Linux Kernel Driver DataBase</a> -
  <a href="http://cateee.net/lkddb/web-lkddb/">web LKDDb index</a>
</p>
</div>

<h1>CONFIG_$conf: $prompt</h1>

<p>Web version of
<a href="http://cateee.net/lkddb/">Linux Kernel Driver DataBase</a></p>

<h2>General informations</h2>

<p>$conf (CONFIG_$conf) is a Linux kernel configuration option of type $type.</p>

<h2>Help text</h2>

<p>$help</p>

<h2>Other informations</h2>

<ul>
  <li>Defined in: $kconf_filename</li>
  $others
</ul>

<h2>Hardware</h2>

$hardware

<h3>LKDDb</h3>

<p>Raw data from LKDDb:</p>
<ul>
$lkddb
</ul>


<h2>Sources</h2>

<ul>
  <li><a href="http://www.kernel.org">Linux Kernel</a>, version $kernel</li>
  <li><a href="http://cateee.net/lkddb/">Linux Kernel Driver DataBase</a> (LKDDb)</li>
  $sources
</ul>

<h2>Notes</h2>

<p><b>Pages under construction</b>, so use with care!</p>
<p>These pages are automatic generated. Sources can be found in ...</p>

<h2>Automatic links from google (and ads)</h2>
<script type="text/javascript"><!--
google_ad_client = "pub-8942588522142995";
//lkddb-links
google_ad_slot = "4558010422";
google_ad_width = 728;
google_ad_height = 15;
//--></script>
<script type="text/javascript"
src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>

<p></p>

<script type="text/javascript"><!--
  google_ad_client = "pub-8942588522142995";
  google_ad_width = 728;
  google_ad_height = 90;
  google_ad_format = "728x90_as";
  google_ad_type = "text_image";
  //2007-10-29: LKDDB
  google_ad_channel = "8963309302";
  google_color_bg = "FFFFCC";
  //-->
</script>

<script type="text/javascript"
  src="http://pagead2.googlesyndication.com/pagead/show_ads.js">
</script>


<div class="foot">
<div class="hnav">
<p>
  Navigation:
  <a href="http://cateee.net/lkddb/">Linux Kernel Driver DataBase</a> -
  <a href="http://cateee.net/lkddb/web-lkddb/">web LKDDb index</a>
</p>
</div>


<!-- SiteSearch Google -->
<form method="get" action="http://www.google.com/custom" target="_top">
<table border="0" bgcolor="#ffffff">
<tr><td nowrap="nowrap" valign="top" align="left" height="32">
<a href="http://www.google.com/">
<img src="http://www.google.com/logos/Logo_25wht.gif" border="0" alt="Google" align="middle"></img></a>
</td>
<td nowrap="nowrap">
<input type="hidden" name="domains" value="cateee.net"></input>
<label for="sbi" style="display: none">Enter your search terms</label>
<input type="text" name="q" size="31" maxlength="255" value="" id="sbi"></input>
<label for="sbb" style="display: none">Submit search form</label>
<input type="submit" name="sa" value="Search" id="sbb"></input>
</td></tr>
<tr>
<td>&nbsp;</td>
<td nowrap="nowrap">
<table>
<tr>
<td>
<input type="radio" name="sitesearch" value="" checked id="ss0"></input>
<label for="ss0" title="Search the Web"><font size="-1" color="black">Web</font></label></td>
<td>
<input type="radio" name="sitesearch" value="cateee.net" id="ss1"></input>
<label for="ss1" title="Search cateee.net"><font size="-1" color="black">cateee.net</font></label></td>
</tr>
</table>
<input type="hidden" name="client" value="pub-8942588522142995"></input>
<input type="hidden" name="forid" value="1"></input>
<input type="hidden" name="channel" value="6039882207"></input>
<input type="hidden" name="ie" value="ISO-8859-1"></input>
<input type="hidden" name="oe" value="ISO-8859-1"></input>
<input type="hidden" name="cof" value="GALT:#008000;GL:1;DIV:#336699;VLC:663399;AH:center;BGC:FFFFFF;LBGC:336699;ALC:0000FF;LC:0000FF;T:000000;GFNT:0000FF;GIMP:0000FF;FORID:1"></input>
<input type="hidden" name="hl" value="en"></input>
</td></tr></table>
</form>
<!-- SiteSearch Google -->


<p>Automatically generated with <code>kconf-db-builder.py</code>,
using kernel $kernel</p>
</div>
</body>
</html>
""")


# read list

def read_list(dict, filename, level):
    "read a .list file into a dictionary of dictionary of (until level)"
    f = open(filename)
    for line in f:
	if line[0] == "#"  or  line.isspace():
	    continue
	fields = line[:-1].split("\t", level)
	rest = fields[-1]
	assert level > 0
	f0 = fields[0]
        if not dict.has_key(f0):
            dict[f0] = {}
	if level == 1:
	    dict[f0] = rest
	else:
	    f1 = fields[1]
	    if not dict[f0].has_key(f1):
	    	dict[f0][f1] = {}
	    if level == 2:
		dict[f0][f1] = rest
	    else:
		assert 0
    f.close()


# ---- parse lkddb ----

lkddb_lines = {}
lkddb_db = {}
lkddb_inverse = {}

def parse_lkddb(filename):
    "read lkddb.list, constructing a CONFIG_ dict"
    f = open(filename)
    for line in f:
	if line[0] == "#"  or  line.isspace():
	    continue
	fields = line.split("\t:: ")
	if len(fields) != 3:
	    print "unknow format of line :", line,
	    assert len(fields) == 3
	ignore, type, rest = fields[0].split("\t", 2)
	for config in fields[1].split(" "):
	    if config == "CONFIG__UNKNOW__":
	        pass
	    conf = config[7:]
	    if not conf:
		############# check and correct
		continue
	    if not lkddb_lines.has_key(conf):
	        lkddb_lines[conf] = [line]
	    else:
	        lkddb_lines[conf].append(line)
	    if not lkddb_db.has_key(conf):
	        lkddb_db[conf] = {type: [rest]}
	    else:
	        if not lkddb_db[conf].has_key(type):
		    lkddb_db[conf][type] = [rest]
		else:
		    lkddb_db[conf][type].append(rest)
	    if not lkddb_inverse.has_key(type):
		lkddb_inverse[type] = {}
	    if not lkddb_inverse[type].has_key(rest):
		lkddb_inverse[type][rest] = [conf]
	    else:
		lkddb_inverse[type][rest].append(conf)

# ---- parse Kconfig files ----

config = {}
def config_add(conf, item, values):
    "add a new item to the config database"
    if not config.has_key(conf):
        config[conf] = {item: [values]}
    else:
        d = config[conf]
        if not d.has_key(item):
             d[item] = [values]
	elif not values in d[item]:
	     d[item].append(values)

def config_get(conf, item):
    "get the values of conf->item"
    if not config.has_key(conf)  or  not config[conf].has_key(item):
	return None
    else:
	return config[conf][item]


kconf_re = re.compile(r"^(?:menu)?config\s+(\w+)\s*\n(.*?)\n[a-z]",
                re.MULTILINE | re.DOTALL)

def parse_kconf(src, filename):
    "read config menu in Kconfig"
    src = src + "\nxxx\n"
    p = 0
    while (True):
	m = kconf_re.search(src, p)
	if not m:
	    break
	p = m.start()+1
	conf, block = m.groups()

    	config_add(conf, "_kconf", filename)
	lines = block.rstrip().split("\n")
	max_item = len(lines)-1
	i = 0
	while(True):
	    if i > max_item:
	        break
	    line = lines[i].strip()
	    if line == "":
	        i+=1
		continue
	    elif line == "help"  or  line == "---help---":
		i+=1
		item = "help"
		value = ""
		help_ident = -1
	    	while(True):
                    if i > max_item:
                        break
		    line = lines[i].rstrip()
		    if line == "":
		        value += "\n"
		    else:
		        line =  line.expandtabs()
		        sline = line.lstrip(" ")
		        ident = len(line) - len(sline)
		        if help_ident == -1:
		    	    help_ident = ident
		        elif ident < help_ident:
		            break
		        value += sline  + "\n"
		    i +=1
	    else:
	        args = line.split()
		item = args[0]
		if len(args) == 1:
		    value = ("",)
		else:
		    value = args[1:]
	    config_add(conf, item, value)
	    i+=1

def kernel_info(kerneldir):
    global kernel_version, kernel_patch, kernel_sub, kernel_extra, kernel_string
    filename = os.path.join(kerneldir, "Makefile")
    f = open(filename)
    src = f.read(512)
    f.close()
    m = re.search(   r"VERSION\s*=\s*(\S+)\s+"+
                  r"PATCHLEVEL\s*=\s*(\S+)\s+"+
                    r"SUBLEVEL\s*=\s*(\S+)\s+"+
                r"EXTRAVERSION\s*=\s*(\S+)\s+", src, re.DOTALL)
    kernel_version, kernel_patch, kernel_sub, kernel_extra = m.groups()
    kernel_string = "%s.%s.%s%s" % (kernel_version, kernel_patch, kernel_sub, kernel_extra)

#--------------
usage = "usage: %prog [options] kernel-dir db-dir"
parser = optparse.OptionParser(usage=usage)
parser.set_defaults(verbose=True, dbfile="lkddb.data")
parser.add_option("-q", "--quiet", dest="verbose",
                    action="store_false",
                    help="don't print warning messages")
parser.add_option("-o", "--output", dest="output",
                    action="store", type="string",
                    help="write warnings to FILE", metavar="FILE")
parser.add_option("-f", "--file", dest="dbfile",
                    action="store", type="string",
                    help="FILE to put the database", metavar="FILE")


(options, args) = parser.parse_args()

if options.output:
    logfile = open(options.output, "w")
else:
    logfile = sys.stdout

if len(args) < 2:
    parser.error("incorrect number of arguments")

kerneldir = args[0]
db_dir = args[1]
if kerneldir[-1] != "/":
    kerneldir += "/"
kerdir_len = len(kerneldir)

dirs = ("arch", "block", "crypto", "drivers", "fs", "init",
	"ipc", "kernel", "lib", "mm", "net", "security", "sound")

print "doing the directory %s and the sub-dirs: %s" % (
 kerneldir, ", ".join(dirs) )

for subdir in dirs:
    for root_full, d_, files in os.walk(os.path.join(kerneldir, subdir)):
        dir = root_full[kerdir_len:]
        for kconf in files:
            if not kconf.startswith("Kconfig"):
                continue
            filename = os.path.join(dir, kconf)
	    f = open(os.path.join(kerneldir, filename))
	    src = f.read()
	    f.close()
	    parse_kconf(src, filename)

dbs = {}
parse_lkddb(os.path.join(db_dir, "lkddb.list"))
read_list(dbs, os.path.join(db_dir, "pci.list"), 2)
read_list(dbs, os.path.join(db_dir, "usb.list"), 2)
read_list(dbs, os.path.join(db_dir, "eisa.list"), 2)
read_list(dbs, os.path.join(db_dir, "zorro.list"), 2)

kernel_info(kerneldir)
now = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())


# -------------------

escapemap = (
	("<", "&lt;"),
	(">", "&gt;"),
	("&", "&amp;"))

def escape(src):
    for c, esc in escapemap:
	src = src.replace(c, esc)
    return src


def extract_key(dict, items):
    for item in items:
	if dict.has_key(item):
	    type = item
	    value = dict[item]
	    break
    else:
	return "", ""
    if value == None:
	value = ""
    return type, value


dir = "web-lkddb/"

config_re = re.compile(r"CONFIG_([^_]\w*)")
help_local_re = re.compile(r"<file:([^>]*)>")

if not os.path.isdir(dir):
    print "could not find in '.' the subdir", dir
    sys.exit(1)

for conf, data in config.iteritems():
    fn = os.path.join(dir, conf+".html")
    f = open(fn, "w")

    out = {
	"conf": conf.strip(),
	"kernel": kernel_string,
	"time": now
    }
    others = ""
    hardware = ""
    sources = ""
    kconf_filename = []
    for kconf in data.get("_kconf", None):
        if not kconf:
	    break
	kconf_filename.append(
	    '<a href="http://lxr.linux.no/source/'+kconf+'">'+kconf+'</a>')
    out["kconf_filename"] = ", ".join(kconf_filename)

    type = []
    prompt = []
    for t in ("bool", "tristate", "string", "hex", "int"):
	if data.has_key(t):
	    type.append(t)
	    for val in data[t]:
	    	if val[0] != "":
		    prompt.append(" ".join(val))
    out["type"]   = "'<i>" + "</i>,<i> ".join(type) + "</i>'"
    out["prompt"] = ", ".join(prompt)
    out["type"] = out["type"].replace("tristate", "tristate (i.e. modulizable)")

    if "tristate" in type:
	if lkddb_db.has_key(conf):
	    lm = []
	    for m in lkddb_db[conf].get("module", []):
		lm.append(m.split("\t",1)[0])
	    if lm:
	        others += ("<li>Module built: <code>" +
			     "</code>,<code> ".join(lm)  +
			   "</code></li>\n")
    
    help = data.get("help", ("(None)",))
    if len(help) > 1:
        s = "There are some alternate helps:</p>\n<h3>help item</h3>\n<p>"
	s += "</p><h3>help item</h3>\n<p>".join(help)
    else:
        s = help[0]
    s = help_local_re.sub(r'<a href="http://lxr.linux.no/source/\1">\1</a>', s)
    out["help"] = s.strip().replace("\n\n", "</p>\n\n<p>")
    
    if lkddb_lines.has_key(conf):
        s = ""
	for line in lkddb_lines[conf]:
	    fields = line.split("\t:: ")
	    fields[1] = config_re.sub(r'<a href="\1.html">CONFIG_\1</a>', fields[1])
	    fields[2] = '<a href="http://lxr.linux.no/source/'+fields[2]+'">'+fields[2]+'</a>' 
	    s += "<li><code>" + " :: ".join(fields) + "</code></li>\n"
    else:
        s = "<li>(None)</li>"
    out["lkddb"] = s

    if lkddb_db.has_key(conf)  and  lkddb_db[conf].has_key("pci"):
	s = "<h3>PCI</h3>\n<p>Numeric ID (from LKDDb) and names (from pci.ids) of recognized devices:</p>\n<ul>\n"
	ids = dbs.get("pci_ids", {})
	for pci in lkddb_db[conf]["pci"]:
	    ss = ""
	    v0, v1, v2, v3, v4 = pci.split(" ")
	    if v0 != "....":
		ss += "vendor: <code>" + v0 + "</code>"
		key = v0
		if ids.has_key(key):
		    ss += ' ("<i>' + escape(ids[key]) + '</i>")'
		if v1 != "....":
		    ss += ", device: <code>" + v1 + "</code>"
		    key += " " + v1
		    if ids.has_key(key):
			ss += ' ("<i>' + escape(ids[key])  + '</i>")'
		    if v2 != "...." and v3 != "....":
                        ss += ", subvendor, subdedvice: <code>" + v2 + "</code>, <code>" + v3 + "</code>"
			key += " " + v2 + " " + v3
                        if ids.has_key(key):
                            ss += ' ("<i>' + escape(ids[key]) + '</i>")'
	    v0, v1, v2 = ( v4[0:2], v4[2:4], v4[4:6])
	    if v0 != "..":
		if ss != "":
		    ss += ", "
                ss += "class: <code>" + v0 + "</code>"
		key = "C " + v0
                if ids.has_key(key):
                    ss += ' ("<i>' + escape(ids[key]) + '</i>")'
                if v1 != "..":
                    ss += ", subclass: <code>" + v1 + "</code>"
		    key += " " + v1
                    if ids.has_key(key):
                        ss += ' ("<i>' + escape(ids[key]) + '</i>")'
                    if v2 != "..":
                        ss += ", prog-if: <code>" + v2 + "</code>"
			key += " " + v2
                        if ids.has_key(key):
                            ss += ' ("<i>' + escape(ids[key]) + '</i>")'
	    if ss:
		c = lkddb_inverse['pci'].get(pci, [])
		c.remove(conf)
		cc = []
		for i in c:
		    cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
		c = ", ".join(cc)
		if c:
		    ss += " (also defined in " + c + ")"
		s += "<li>" + ss + "</li>\n"
	hardware += s + "</ul>\n\n"
	sources += '<li>The <a href="http://pciids.sourceforge.net/">Linux PCI ID Repository</a> (pci.ids)</li>\n'

    if lkddb_db.has_key(conf)  and  lkddb_db[conf].has_key("usb"):
        s = "<h3>USB</h3>\n<p>Numeric ID (from LKDDb) and names (from usb.ids) of recognized devices:</p>\n<ul>\n"
	ids = dbs.get("usb_ids", {})
        for usb in lkddb_db[conf]["usb"]:
            ss = ""
            v0, v1, v2, v3, v4, v5 = usb.split(" ")
            if v0 != "....":
                ss += "vendor: <code>" + v0 + "</code>"
		key = v0
                if ids.has_key(key):
                    ss += ' ("<i>' + escape(ids[key]) + '</i>")'
                if v1 != "....":
                    ss += ", device: <code>" + v1 + "</code>"
		    key += " " + v1
                    if ids.has_key(key):
                        ss += ' ("<i>' + escape(ids[key]) + '</i>")'
	    # interface ???????????
            v0, v1, v2 = ( v3[0:2], v3[2:4], v3[4:6])
            if v0 != "..":
                if ss != "":
                    ss += ", "
                ss += "device class: <code>" + v0 + "</code>"
                key = "C " + v0
                if ids.has_key(key):
                    ss += ' ("<i>' + escape(ids[key]) + '</i>")'
                if v1 != "..":
                    ss += ", device subclass: <code>" + v1 + "</code>"
		    key += " " + v1
                    if ids.has_key(key):
                        ss += ' ("<i>' + escape(ids[key]) + '</i>")'
                    if v2 != "..":
                        ss += ", device prog-if: <code>" + v2 + "</code>"
			key += " " + v2
                        if ids.has_key(key):
                            ss += ' ("<i>' + escape(ids[key]) + '</i>")'
	    # interface class ???????????????
            if ss:
                c = lkddb_inverse['usb'].get(usb, [])
                c.remove(conf)
                cc = []
                for i in c:
                    cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
                c = ", ".join(cc)
                if c:
                    ss += " (also defined in " + c + ")"
                s += "<li>" + ss + "</li>\n"
        hardware += s + "</ul>\n\n"
        sources += '<li>The <a href="http://www.linux-usb.org/">USB Vendor/Device IDs list</a> (usb.ids)</li>\n'

    if lkddb_db.has_key(conf)  and  lkddb_db[conf].has_key("eisa"):
	s = "<h3>EISA</h3>\n<p>ID (from LKDDb) and names (from eisa.ids) of recognized devices:</p>\n<ul>\n"
	ids = dbs.get("eisa_ids", {})
	for eisa in lkddb_db[conf]["eisa"]:
	    name = eisa[1:-1]
	    s += "<li>" + escape(name)
	    if ids.has_key(name):
		s += " (<i>" + escape(ids[name]) + "</i>)"
            c = lkddb_inverse['eisa'].get(eisa, [])
	    c.remove(conf)
            cc = []
            for i in c:
                cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
            c = ", ".join(cc)
            if c:
                s += " (also defined in " + c + ")"
	    s += "</li>\n"
	hardware += s + "</ul>\n\n"
	sources += "<li>eisa.ids from kernel sources</li>\n"

    if lkddb_db.has_key(conf)  and  lkddb_db[conf].has_key("zorro"):
        s = "<h3>Zorro</h3>\n<p>ID (from LKDDb) and names (from zorro.ids) of recognized devices:</p>\n<ul>\n"
        ids = dbs.get("zorro_ids", {})
        for zorro in lkddb_db[conf]["zorro"]:
            ss = ""
            v0, v1 = zorro.split(" ")
            if v0 != "....":
                ss += "manufacturer: <code>" + v0 + "</code>"
                key = v0
                if ids.has_key(key):
                    ss += ' ("<i>' + escape(ids[key]) + '</i>")'
                if v1 != "....":
                    ss += ", product: <code>" + v1 + "</code>"
                    key += " " + v1
            if ss:
                c = lkddb_inverse['zorro'].get(zorro, [])
		c.remove(conf)
                cc = []
                for i in c:
                    cc.append('<a href="'+i+'.html">CONFIG_'+i+'</a>')
                c = ", ".join(cc)
                if c:
                    ss += " (also defined in " + c + ")"
                s += "<li>" + ss + "</li>\n"
	hardware += s + "</ul>\n\n"
	sources += "<li>zorro.ids from kernel sources</li>\n"

    out["others"] = others
    out["hardware"] = hardware
    out["sources"] = sources
    f.write(page.substitute(out))
    f.close()

print "done %s elements" % len(config)

# ---- index builder ----

hash = {}
for conf in config.keys():
    c = conf[0]
    if not c.isupper():
        c = "0-9"
    if not hash.has_key(c):
        hash[c] = [conf]
    else:
	hash[c].append(conf)


index_page = string.Template("""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="content-type" content="text/html; charset=utf-8" />
  <link href="http://cateee.net/template/lkddb.css" rel="stylesheet" type="text/css" />
  <title>Linux Kernel Driver Database: '$key' index</title>
</head>

<body xml:lang="en" lang="en">

<div class="hnav">
<p>
  Navigation:
  <a href="http://cateee.net/lkddb/">Linux Kernel Driver DataBase</a> -
  <a href="http://cateee.net/lkddb/web-lkddb/">web LKDDb index</a>
</p>
</div>

<h1>LKDDB '$key' index</h1>

<p>Index of Linux kernel configurations in '$key'</p>

<ul>
$list
</ul>

<div class="foot">
<div class="hnav">
<p>
  Navigation:
  <a href="http://cateee.net/lkddb/">Linux Kernel Driver DataBase</a> -
  <a href="http://cateee.net/lkddb/web-lkddb/">web LKDDb index</a>
</p>
</div>

<p>Automatically generated with <code>kconf-db-builder.py</code>,
at $time.</p>
</div>
</body>
</html>
""")

main = {}
for key, values in hash.iteritems():
    fn = os.path.join(dir, "index_" + key + ".html")
    f = open(fn, "w")
    s = ""
    values.sort()
    for val in values:
        s += '<li><a href="%s.html">CONFIG_%s</a></li>\n' % (val, val)
    f.write(index_page.substitute(
	{"key": key,
	"list": s,
        "kernel": kernel_string,
        "time": now}))
    f.close()
    main[key] = '<li><a href="index_%s.html">%s</a></li>\n' % (key, key)

keys = main.keys()
keys.sort()
main_index = ""
for key in keys:
    main_index += main.get(key, "")

fn = os.path.join(dir, "index.html")
f = open(fn, "w")
f.write(index_page.substitute(
	{"key": "main",
	"list": main_index,
	"kernel": kernel_string,
	"time": now}))
f.close()

