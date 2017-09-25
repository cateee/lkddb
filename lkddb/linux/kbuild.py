#!/usr/bin/python
#: lkddb/linux/kbuild.py : scanners for kernel build infrastructure 
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import os
import os.path
import re
import subprocess
import fnmatch
import lkddb

# kernel version and name

class kver(lkddb.browser):

    def __init__(self, kver_table, tree):
        lkddb.browser.__init__(self, "kver")
	self.table = kver_table
	self.tree = tree
	self.kerneldir = tree.kerneldir

    def scan(self):
        "Makefile, scripts/setlocalversion -> return (ver_number, ver_string, released)" 
	lkddb.browser.scan(self)
	version_dict = self.tree.version_dict
	self.table.add_row((version_dict['version'], version_dict['patchlevel'], version_dict['sublevel'],
			    version_dict['numeric2'], version_dict['numeric3'],
			    version_dict['str'], version_dict['name'] ))


# parse kbuild files (Makefiles) and extract the file dependencies

# comment are remover; \ line are merged
kbuild_normalize = re.compile(
	r"(#.*$|\\\n)", re.MULTILINE)
kbuild_includes = re.compile(
	r"^-?include\s+\$[\(\{]srctree[\)\}]/(.*)$", re.MULTILINE)
kbuild_rules = re.compile(
	r"^([A-Za-z0-9-_]+)-([^+=: \t\n]+)\s*[:+]?=[ \t]*(.*)$", re.MULTILINE)

ignore_rules_set = frozenset(
#    ("init", "drivers", "net", "libs", "core", "obj", "lib",
    ("ccflags", "cflags", "cpuflags"))

#build = frozenset('init', 'drivers', 'net', 'libs', 'core')

class makefiles(lkddb.browser):
    def __init__(self, firmware_table, kerneldir, dirs):
        lkddb.browser.__init__(self, "kmake")
        self.firmware_table = firmware_table
        self.kerneldir = kerneldir
	self.dirs = dirs
        # dictionary of CONFIG_ dependencies on files (from Makefile)
        # format: filename.c: (CONFIG_FOO, CONFIG_BAR)
        self.dependencies = {}
        # format: filename.c: (virtual-filename-objs.c, ...)
        self.dep_aliases = {}
        # the inverse; format CONFIG_FOO: name  (used for module, so single name)
        self.modules = {}

    def scan(self):
	lkddb.browser.scan(self)
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.kerneldir)
            for subdir in self.dirs:
                if subdir == "arch":
                    for arch in os.listdir("arch/"):
                        mk2 = os.path.join("arch/", arch)
                        self.__parse_kbuild(mk2, set(()), 1)
		elif subdir.startswith("arch/") and subdir.count("/") == 1:
		    self.__parse_kbuild(subdir, set(()), 1)
                else:
                    self.__parse_kbuild(subdir, set(()), 0)
        finally:
            os.chdir(orig_cwd)


    def __parse_kbuild(self, subdir, deps, main):
	# main = 0: normal case -> path relatives
        # main = 1: arch/xxx/Makefile -> path from root
        # main = 2: arch/xxx/Kbuild -> path relative, don't parse Makefile
        try:
            files = os.listdir(subdir)
        except OSError:
            lkddb.log.log("parse_kbuild: not a directory: %s" % subdir)
            return
        if main != 1  and  "Kbuild" in files:
	    f = open(os.path.join(subdir, 'Kbuild'))
	    src = kbuild_normalize.sub(" ", f.read())
	    f.close()
	else:
	    src = ""
        if main != 2  and  "Makefile" in files:
            f = open(os.path.join(subdir, 'Makefile'))
            src += '\n' + kbuild_normalize.sub(" ", f.read())
            f.close()
        if not src:
            lkddb.log.log("No Makefile/Kbuild in %s" % subdir)
            return

	# includes
	while(True):
	    m = kbuild_includes.search(src)
	    if not m:
		break
	    mk2 = m.group(1)
            if not os.path.isfile(mk2):
	        lkddb.log.log("parse_kbuild: could not find included file (from %s): %s" %
                                (subdir, mk2))
		src = src[:m.start()] + "\n" + src[m.end():]
		continue
	    f = open(mk2)
	    src2 = kbuild_normalize.sub(" ", f.read())
	    f.close()
	    src = src[:m.start()] + "\n" + src2 + "\n" + src[m.end():]

        if main == 1:
            base_subdir = ""
        else:
            base_subdir = subdir

	self.__parse_kbuild_lines(base_subdir, deps, src)

        if main == 1:
           self.__parse_kbuild(subdir, deps, 2)

		
    def __parse_kbuild_alias(self, subdir, rule, dep, files):
        for f in files.split():
            fn = os.path.normpath(os.path.join(subdir, f))
            if f[-2:] == ".o":
                fc = fn[:-2]+".c"
                virt = [ os.path.join(subdir, rule+".c") ]
                if fc in self.dep_aliases:
                    virt.extend(self.dep_aliases[fc])
                self.dep_aliases[fc] = virt
            elif f[-1] == "/":
                self.__parse_kbuild(fn, dep, 0)


    def __parse_kbuild_lines(self, subdir, deps, src):

	# rule-$(dep): files
        for (rule, dep, files) in kbuild_rules.findall(src):
            d = deps.copy()
            if not files:
                pass
	    if rule == "clean":
		continue
            if dep in ("y", "m"):
                pass
            elif (dep[:9] == '$(CONFIG_' and dep[-1] == ')') or (
                  dep[:9] == '${CONFIG_' and dep[-1] == '}'):
                i = dep[:-1].find(')', 2)
                if i > 0 and dep[i+1:i+10] == "$(CONFIG_":
                    d.add(dep[2:i])
                    self.modules[dep[2:i]] = files
                    d.add(dep[i+3:-1])
                    self.modules[dep[i+3:-1]] = files
                else:
                    d.add(dep[2:-1])
		    if rule == "fw-shipped":
			for f in files.split():
			    if f.find("$") > -1:
				lkddb.log.log("this firmware include indirect firmwares '%s': '%s'" %
					(dep[2:-1], os.path.join(subdir,f)))
			    else:
			        self.firmware_table.add_row((dep[2:-1], os.path.join(subdir,f)))
			continue
		    else:
                        self.modules[dep[2:-1]] = files
            elif dep == "objs":
                self.__parse_kbuild_alias(subdir, rule, dep, files)
                continue
            else:
                lkddb.log.log("parse_kbuild: unknow dep in %s: '%s'" % (subdir, dep))
                continue

            for f in files.split():
		fn = os.path.join(subdir, f)
                if f[-1] == "/":
		    fn = os.path.join(subdir, f[:-1])
                    self.__parse_kbuild(fn, d, 0)
                elif f[-2:] == ".o":
                    fc = fn[:-2]+".c"
                    v = d.copy()
                    if fc in self.dependencies:
                        v.update(self.dependencies[fc])
                    self.dependencies[fc] = v
                else:
                    lkddb.log.log_extra(
			"parse_kbuild: unknow target in '%s': '%s, was %s'" % (
			subdir, f, (rule, dep, files)))

            if not rule in ignore_rules_set:
                self.__parse_kbuild_alias(subdir, rule, d, files)

# -----

    def _list_dep_rec(self, fn, dep, passed):
        deps = self.dependencies.get(fn, None)
        if deps != None:
            dep.update(deps)
        aliases = self.dep_aliases.get(fn, None)
        if aliases != None:
            for alias in aliases:
                if alias in passed:
                    continue
                else:
                    passed.add(alias)
                dep.update(self._list_dep_rec(alias, dep, passed))
        return dep

    def list_dep(self, fn):
        dep = set()
        passed = set([fn])
        self._list_dep_rec(fn, dep, passed)
        if not dep:
            return set( ["CONFIG__UNKNOW__"] )
        return dep

# parse kconfig files
# Note: one sources, two devices

tristate_re = re.compile(r'^config\s*(\w+)\s+tristate\s+"(.*?[^\\])"',
							re.DOTALL | re.MULTILINE)
kconf_re = re.compile(r"^(?:menu)?config\s+(\w+)\s*\n(.*?)\n[a-z]",
					                re.MULTILINE | re.DOTALL)
# context
C_TOP=0; C_CONF=1; C_HELP=2


class kconfigs(lkddb.browser):

    def __init__(self, kconf_table, module_table, kerneldir, dirs, makefiles, tree):
        lkddb.browser.__init__(self, "kconfigs")
	self.kconf_table = kconf_table
	self.module_table = module_table
        self.kerneldir = kerneldir
	self.dirs = dirs
	self.makefiles = makefiles
	self.tree = tree
	# two kind of "tables": config and module

    def scan(self):
	old_kernel = (self.tree.version < 0x020600)  ### find exact version
	lkddb.browser.scan(self)
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.kerneldir)
            for subdir in self.dirs:
                for dir, d_, files in os.walk(subdir):
		    if old_kernel:
                        for kconf in fnmatch.filter(files, "Config.in"):
                            filename = os.path.join(dir, kconf)
                            lkddb.log.log_extra("Kconfig (<2.6) doing: " + filename)
                            self.__parse_config_in(filename)
		    else:
                        for kconf in fnmatch.filter(files, "Kconfig*"):
       	                    filename = os.path.join(dir, kconf)
                	    lkddb.log.log_extra("Kconfig (>=2.6) doing: " + filename)
                            self.__parse_kconfig(filename)
        finally:
            os.chdir(orig_cwd)

    def finalize(self):
	lkddb.browser.finalize(self)

    def __parse_kconfig(self, filename):
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
            #if "#" in args:
            #    args = args.split("#", 1)[0]
            if tok in frozenset(("menu", "endmenu", "source", "if", "endif", "endchoice", "mainmenu")):
                if context == C_CONF:
                    self.__kconf_save(config, dict, type, descr, depends, help, filename)
                context = C_TOP
                continue
            if tok in frozenset(("config", "menuconfig", "choice")):
                if context == C_CONF:
                    self.__kconf_save(config, dict, type, descr, depends, help, filename)
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
                    lkddb.log.log(
			"kconfig: error: help out of context (%s), in %s, after '%s'" %
                               				(context, filename, config))
                context = C_HELP
                ident = -1
                continue
            if tok in frozenset(("bool", "boolean", "tristate", "string", "hex", "int")):
                if tok == "boolean":
                    tok = "bool"
                type = tok
                if not args or args[0] == "#":
                    descr = ""
                else:
                    div = args[0]
                    if not (div == '"'  or  div == "'"):
                        descr = args
                        lkddb.log.log("kconfig: bad line in %s %s: '%s'" %
								(filename, config, line))
                    else:
                        if div == '"':
                            args = args.replace('\\"', "'").replace("\\'", "'")
                            s = args.split(div)
                            descr = s[1]
                        else:
                            args = args.replace('\\"', '"').replace("\\'", '"')
                            s = args.split(div)
                            descr = s[1].replace('"', "'")
                        if len(s) < 3:
                            lkddb.log.log("kconfig: bad line in %s %s: '%s': args=<%s>, s=%s" %
                                                                (filename, config, line, args, s))
                            assert False
                        else:
                            d = s[2].split()
                            if len(d) > 1  and  d[0] == "if":
                                depends.append(" ".join(d[1:]))
            if tok in frozenset(("default", "def_bool", "def_tristate")):
                if tok[3] == "_":
                    type = tok[4:]
                    descr = ""
                if "#" in args:
                    args = args.split("#", 1)[0]
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
               if "#" in args:
                    args = args.split("#", 1)[0]
               d = args.split()
               if len(d) > 1  and  d[0] == "on":
                    depends.append(" ".join(d[1:]))
               else:
                    assert "false"
            if not context == C_CONF:
                # e.g. depents after "menu" or prompt and default after "choice"
                continue
            dict[tok] = args
        if context == C_CONF  or  context == C_HELP:
            self.__kconf_save(config, dict, type, descr, depends, help, filename)


    def __kconf_save(self, config, dict, type, descr, depends, help, filename):
        if not type:  # e.g. on 'choice'
            return
        config = "CONFIG_" + config
        if depends:
            if len(depends) > 1:
                depends = "(" +   ")  &&  (".join(depends)  + ")"
            else:
                depends = depends[0]
        else:
            depends = ""
	self.kconf_table.add_row((type, descr, depends, help.strip(), config, filename))

        if type == "tristate"  or  type == "def_tristate":
	    mod = self.makefiles.modules.get(config, None)
            if mod:
		if mod.find(" ") > -1:
		    lkddb.log.log("warning: multiple modules in '%s': '%s" %
				(config, mod))
                for name in mod.split():
                    if not name.endswith(".o"):
                        if name[-1] == "/":
                            lkddb.log.log(
				"Kconfig: name '%s' doesn't end with '.o (%s from %s)"
							% (name, config, filename))
                        continue
		    self.module_table.add_row((name[:-2], descr, config, filename))
            else:
                lkddb.log.log("kconfig: could not find the module obj of %s from %s" % (config, filename))

