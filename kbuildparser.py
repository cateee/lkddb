#!/usr/bin/python
#:  kbuildparser.py : parser of kbuild infrastructure
#
#  Copyright (c) 2007,2008  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

# parse kbuild files (Makefiles) and extract the file dependencies


import sys, os, os.path, re
import utils, devicetables

# --- --- --- --- #
# parse Makefile for file dependencies

# dictionary of CONFIG_ dependencies on files (from Makefile)
# format: filename.c: (CONFIG_FOO, CONFIG_BAR)
dependencies = {}
# the inverse; format CONFIG_FOO: name  (used for module, so single name)
modules = {}
# format: filename.c: (virtual-filename-objs.c, ...)
dep_aliases = {}

kbuild_normalize = re.compile(r"(#.*$|\\[ \t]*\n)", re.MULTILINE)
kbuild_includes = re.compile(r"^\s*include\s+\$[\(\{]srctree[\)\}]/(.*)$", re.MULTILINE)
ignore_rules_set = frozenset(
#    ("init", "drivers", "net", "libs", "core", "obj", "lib",
     ("cflags", "cpuflags"))


def parse_kbuild(subdir, deps=None):
    try:
        files = os.listdir(subdir)
    except OSError:
	utils.log("parse_kbuild: I don't know the directory %s" % subdir)
	return
    if "Makefile" in files:
        source = "Makefile"
    elif "Kbuild" in files:
        source = "Kbuild"
    elif deps == None:
	utils.log("No Makefile in %s, recursing..." % subdir)
        for dir in files:
            if os.path.isdir(os.path.join(subdir, dir)):
                parse_kbuild(os.path.join(subdir, dir), deps)
        return
    else:
        utils.log("No Makefile in %s" % subdir)
	return
    mk = os.path.normpath(os.path.join(subdir, source))

    f = open(mk)
    src = kbuild_normalize.sub(" ", f.read())
    f.close()
    for incl in kbuild_includes.findall(src):
	mk2 = os.path.normpath(incl)
	# print "check--------------", mk, "includes", mk2 #######################################3
	if not os.path.isfile(mk2):
	    utils.log("parse_kbuild: could not find included file (from %s): %s" % (mk, mk2))
	    return
	f = open(mk2)
	src += " " + kbuild_normalize.sub(" ", f.read())
	f.close()
    if deps == None:
	deps = set()
    if subdir.startswith("arch/")  and  subdir.count("/") == 1:
	base_subdir = ""
    else:
	base_subdir = subdir
    parse_kbuild_lines(base_subdir, deps, src)


def parse_kbuild_alias(subdir, deps, rule, dep, files):
   for f in files.split():
	fn = os.path.normpath(os.path.join(subdir, f))
	if f[-2:] == ".o":
	    fc = fn[:-2]+".c"
	    virt = [ os.path.join(subdir, rule+".c") ]
            if dep_aliases.has_key(fc):
                virt.extend(dep_aliases[fc])
            dep_aliases[fc] = virt
	elif f[-1] == "/":
	    parse_kbuild(fn, dep)

kbuild_rules = re.compile(r"^([A-Za-z0-9-_]+)-([^+=: \t\n]+)\s*[:+]?=[ \t]*(.*)$", re.MULTILINE)

def parse_kbuild_lines(subdir, deps, src):
    for (rule, dep, files) in kbuild_rules.findall(src):
	d = deps.copy()
	if not files:
	    pass
	# rule-$(dep): file.o
        if dep in ("y", "m") or  rule == "clean":
            pass
        elif (dep[:9] == '$(CONFIG_' and dep[-1] == ')') or (
	      dep[:9] == '${CONFIG_' and dep[-1] == '}'):
	    i = dep[:-1].find(')', 2)
	    if i > 0 and dep[i+1:i+10] == "$(CONFIG_":
		d.add(dep[2:i])
		modules[dep[2:i]] = files
		d.add(dep[i+3:-1])
		modules[dep[i+3:-1]] = files
	    else:
                d.add(dep[2:-1])
	        modules[dep[2:-1]] = files
	elif dep == "objs":
	    parse_kbuild_alias(subdir, deps, rule, dep, files)
	    continue
        else:
            utils.log("parse_kbuild: unknow dep in %s: '%s'" % (subdir, dep))
            continue

        for f in files.split():
            fn = os.path.join(subdir, f)
            if f[-1] == "/":
                parse_kbuild(fn, d)
            elif f[-2:] == ".o":
                fc = fn[:-2]+".c"
		v = d.copy()
                if dependencies.has_key(fc):
		    v.update(dependencies[fc])
                dependencies[fc] = v
            else:
                utils.log_extra("parse_kbuild: unknow 'make target' in %s: '%s'" % (subdir, f))

        if not rule in ignore_rules_set:
	    parse_kbuild_alias(subdir, deps, rule, d, files)


def list_dep_rec(fn, dep, passed):
    if dep == None:
	dep = set()
    if dependencies.has_key(fn):
        dep.update(dependencies[fn])
    if dep_aliases.has_key(fn):
	for alias in dep_aliases[fn]:
	    if alias in passed:
		continue
	    else:
		passed.add(alias)
	    dep.update(list_dep_rec(alias, dep, passed))
    return dep


def list_dep(fn):
    dep = set()
    passed = set([fn])
    list_dep_rec(fn, dep, passed)
    if not dep:
	return set( ["CONFIG__UNKNOW__"] )
    return dep

# -----------------


tristate_re = re.compile(r'^config\s*(\w+)\s+tristate\s+"(.*?[^\\])"', re.DOTALL | re.MULTILINE)

kconf_re = re.compile(r"^(?:menu)?config\s+(\w+)\s*\n(.*?)\n[a-z]",
                re.MULTILINE | re.DOTALL)

C_TOP=0; C_CONF=1; C_HELP=2

def parse_kconfig(filename):
    "read config menu in Kconfig"
    f = open(filename)
    context = C_TOP
    config = None
    depends = []
    for line in f:
	line = line.expandtabs()
	if context == C_HELP:
	    ident_new = len(line) - len(line.lstrip())
	    if ident < 0:
	        ident = ident_new
	    if ident_new >= ident  or  line.strip() == "":
	        help += line.strip() + "\n"
	        continue
	    context = C_CONF
	line = line.strip()
	if len(line) == 0  or  line[0] == "#":
	    continue
	try:
	    tok,args = line.split(None, 1)
	except:
	    tok = line ; args = ""
	if tok in frozenset(("menu", "endmenu", "source", "if", "endif", "endchoice", "mainmenu")):
            if context == C_CONF:
                kconf_save(config, dict, type, descr, depends, help, filename)
	    context = C_TOP
	    continue
	if tok in frozenset(("config", "menuconfig", "choice")):
	    if context == C_CONF:
		kconf_save(config, dict, type, descr, depends, help, filename)
	    else:
	        context = C_CONF
	    config = args
	    help = ""
	    dict = {}
	    type = None
	    descr = ""
	    depends = []
	    continue
	if tok in frozenset(("help", "---help---")):
	    if context != C_CONF:
		help = ""
		utils.log("kconfig: error help out of context (%s), in %s, after '%s'" % (
				context, filename, config))
	    context = C_HELP
	    ident = -1
	    continue
	if tok in frozenset(("bool", "tristate", "string", "hex", "int")):
	    type = tok
	    if not args:
		descr = ""
	    else:
		div = args[0]
		if not (div == '"'  or  div == "'"):
		    descr = args
		    print "kconfig: bad line in %s %s: '%s'" % (filename, config, line)
		else:
	            if div == '"':
        	        args = args.replace('\\"', "'").replace("\\'", "'")
                	s =  args.split(div)
	                descr = s[1]
        	    else:
                	args = args.replace('\\"', '"').replace("\\'", '"')
	                s = args.split(div)
        	        descr = s[1].replace('"', "'")
                    d = s[2].split()
                    if len(d) > 1  and  d[0] == "if":
                        depends.append(" ".join(d[1:]))
        if tok in frozenset(("default", "def_bool", "def_tristate")):
	    if tok[3] == "_":
		type = tok[4:]
		descr = ""
            s = args.split('if')
	    if len(s) > 1:
		d = s[1].split()
                depends.append(" ".join(d))
        if tok == "prompt":
	    div = args[0]
	    assert div == '"'  or  div == "'"
	    if div == '"':
		args = args.replace('\\"', "'").replace("\\'", "'")
		s =  args.split(div)
		descr = s[1]
	    else:
		args = args.replace('\\"', '"').replace("\\'", '"')
		s = args.split(div)
		descr = s[1].replace('"', "'")
            d = s[2].split()
            if len(d) > 1  and  d[0] == "if":
                depends.append(" ".join(d[1:]))
  	if tok == "depends":
	   d = args.split()
	   if len(d) > 1  and  d[0] == "on":
		depends.append(" ".join(d[1:]))
	   else:
		assert "false"
	if not context == C_CONF:
	    # e.g. depents after "menu" or prompt and default after "choice"
	    continue
	dict[tok] = args
    if context == C_CONF:
	kconf_save(config, dict, type, descr, depends, help, filename)


def kconf_save(config, dict, type, descr, depends, help, filename):
    if not type:  # e.g. on 'choice'
	return
    c = utils.conn.cursor()
    config = "CONFIG_" + config
    config_id = utils.get_config_id(config)
    filename_id = utils.get_filename_id(filename)
    if depends:
	if len(depends) > 1:
	    depends = '(' +   ")  &&  (".join(depends)  + ')'
	else:
	    depends = depends[0]
    else:
	depends = ""
    kkey_id = key_id[type]
    c.execute("INSERT OR IGNORE INTO kitems (config_id,filename_id,kkey_type,descr,depends,help) VALUES (?,?,?,?,?,?);",
		(config_id, filename_id, kkey_id, descr, depends, help.strip()))
    utils.conn.commit()

    if type == "tristate"  or  type == "def_tristate":
        if modules.has_key(config):
            for name in modules[config].split():
                if not name.endswith(".o"):
                    if name[-1] == "/":
                        utils.log("Kconfig: name %s does'n ends with '.o (%s from %s)" % (
                            name, config, filename))
                    continue
		dict = {'name': name[:-2], 'descr': descr}
	        utils.devices_add(devicetables.module_scanner, dict, (config,), filename)
        else:
            utils.log("kconfig: could not find the module obj of %s from %s" % (config, filename))


key_id = {}
def kconfig_init():
    c = utils.conn.cursor()
    for k in frozenset(("bool", "tristate", "string", "hex", "int")):
        c.execute("INSERT OR IGNORE INTO kkeys (key) VALUES (?);", (k,))
    for kkey_id, key in c.execute("SELECT kkey_id, key FROM kkeys;").fetchall():
        key_id[key] = kkey_id
    utils.conn.commit()

