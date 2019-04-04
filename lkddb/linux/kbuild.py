#!/usr/bin/python
#: lkddb/linux/kbuild.py : scanners for kernel build infrastructure
#
#  Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import os
import os.path
import re
import fnmatch
import logging
import sys

import lkddb

logger = logging.getLogger(__name__)


# kernel version and name

class kver(lkddb.Browser):
    def __init__(self, kver_table, tree):
        super().__init__("kver")
        self.table = kver_table
        self.tree = tree
        self.kerneldir = tree.kerneldir

    def scan(self):
        """Makefile, scripts/setlocalversion -> return (ver_number, ver_string, released)"""
        lkddb.Browser.scan(self)
        version_dict = self.tree.version_dict
        self.table.add_row((version_dict['version'], version_dict['patchlevel'], version_dict['sublevel'],
                            version_dict['numeric2'], version_dict['numeric3'],
                            version_dict['str'], version_dict['name']))


# parse kbuild files (Makefiles) and extract the file dependencies

# comment are removed; \ line are merged
kbuild_normalize = re.compile(
    r"(#.*$|\\\n)", re.MULTILINE)
kbuild_includes = re.compile(
    r"^-?include\s+\$[({]srctree[)}]/(.*)$", re.MULTILINE)
kbuild_rules = re.compile(
    r"^([-A-Za-z0-9_]+)-([^+=: \t\n]+)\s*[:+]?=[ \t]*(.*)$", re.MULTILINE)

ignore_rules_set = frozenset(
    ("clean", "ccflags", "cflags", "aflags", "asflags", "mflags", "cpuflags", "subdir-ccflags", "extra"))


class makefiles(lkddb.Browser):
    def __init__(self, firmware_table, kerneldir, dirs):
        super().__init__("kmake")
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
        # parsed subdirs, with count
        self.parsed_subdirs = {}

    def scan(self):
        lkddb.Browser.scan(self)
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
        if self.parsed_subdirs.get(subdir, 0) > 5:
            return
        self.parsed_subdirs[subdir] = self.parsed_subdirs.get(subdir, 0) + 1
        try:
            files = os.listdir(subdir)
        except OSError:
            logger.warning("parse_kbuild: not a directory: %s" % subdir)
            return
        if main != 1 and "Kbuild" in files:
            f = open(os.path.join(subdir, 'Kbuild'), encoding='utf8', errors='replace')
            src = kbuild_normalize.sub(" ", f.read())
            f.close()
        else:
            src = ""
        if main != 2 and "Makefile" in files:
            f = open(os.path.join(subdir, 'Makefile'), encoding='utf8', errors='replace')
            src += '\n' + kbuild_normalize.sub(" ", f.read())
            f.close()
        if not src:
            logger.warning("No Makefile/Kbuild in %s" % subdir)
            return

        # includes
        while True:
            m = kbuild_includes.search(src)
            if not m:
                break
            mk2 = m.group(1)
            if not os.path.isfile(mk2):
                logger.warning("parse_kbuild: could not find included file (from %s): %s" %
                               (subdir, mk2))
                src = src[:m.start()] + "\n" + src[m.end():]
                continue
            f = open(mk2, encoding='utf8', errors='replace')
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
                fc = fn[:-2] + ".c"
                virt = [os.path.join(subdir, rule + ".c")]
                if fc in self.dep_aliases:
                    virt.extend(self.dep_aliases[fc])
                self.dep_aliases[fc] = virt
            elif f[-1] == "/":
                self.__parse_kbuild(fn, dep, 0)

    def __parse_kbuild_lines(self, subdir, deps, src):
        # rule-$(dep): files
        for (rule, dep, files) in kbuild_rules.findall(src):
            d = deps.copy()
            if not files or files.startswith('-'):  # compiler options
                continue
            if rule in ignore_rules_set:
                continue
            if dep in ("y", "m"):
                pass
            elif (dep[:9] == '$(CONFIG_' and dep[-1] == ')') or (
                            dep[:9] == '${CONFIG_' and dep[-1] == '}'):
                i = dep[:-1].find(')', 2)
                if i > 0 and dep[i + 1:i + 10] == "$(CONFIG_":
                    d.add(dep[2:i])
                    self.modules[dep[2:i]] = files
                    d.add(dep[i + 3:-1])
                    self.modules[dep[i + 3:-1]] = files
                else:
                    d.add(dep[2:-1])
                    if rule == "fw-shipped":
                        for f in files.split():
                            if f.find("$") > -1:
                                logger.warning("this firmware include indirect firmwares '%s': '%s'" %
                                               (dep[2:-1], os.path.join(subdir, f)))
                            else:
                                self.firmware_table.add_row((dep[2:-1], os.path.join(subdir, f)))
                        continue
                    else:
                        self.modules[dep[2:-1]] = files
            elif dep == "objs":
                self.__parse_kbuild_alias(subdir, rule, dep, files)
                continue
            else:
                logger.warning("parse_kbuild: unknown dep in %s: '%s'" % (subdir, dep))
                continue

            for f in files.split():
                fn = os.path.join(subdir, f)
                if f[-1] == "/":
                    fn = os.path.join(subdir, f[:-1])
                    self.__parse_kbuild(fn, d, 0)
                elif f[-2:] == ".o":
                    fc = fn[:-2] + ".c"
                    v = d.copy()
                    if fc in self.dependencies:
                        v.update(self.dependencies[fc])
                    self.dependencies[fc] = v
                else:
                    logger.info("parse_kbuild: unknown target in '%s': '%s, was %s'" %
                                (subdir, f, (rule, dep, files)))

            self.__parse_kbuild_alias(subdir, rule, d, files)

            # -----

    def _list_dep_rec(self, fn, dep, passed):
        deps = self.dependencies.get(fn, None)
        if deps is not None:
            dep.update(deps)
        aliases = self.dep_aliases.get(fn, None)
        if aliases is not None:
            for alias in aliases:
                if alias in passed:
                    continue
                else:
                    passed.add(alias)
                dep.update(self._list_dep_rec(alias, dep, passed))
        return dep

    def list_dep(self, fn):
        dep = set()
        passed = {fn}
        self._list_dep_rec(fn, dep, passed)
        if not dep:
            return {"CONFIG__UNKNOWN__"}
        return dep


# parse kconfig files
# Note: one sources, two devices

tristate_re = re.compile(r'^config\s*(\w+)\s+tristate\s+"(.*?[^\\])"', re.DOTALL | re.MULTILINE)
kconf_re = re.compile(r"^(?:menu)?config\s+(\w+)\s*\n(.*?)\n[a-z]", re.MULTILINE | re.DOTALL)
# context
C_TOP = 0
C_CONF = 1
C_HELP = 2


class kconfigs(lkddb.Browser):
    def __init__(self, kconf_table, module_table, kerneldir, dirs, makefiles, tree):
        super().__init__("kconfigs")
        self.kconf_table = kconf_table
        self.module_table = module_table
        self.kerneldir = kerneldir
        self.dirs = dirs
        self.makefiles = makefiles
        self.tree = tree
        # two kind of "tables": config and module

    def scan(self):
        old_kernel = (self.tree.version_dict['numeric'] < 0x020600)  # find exact version
        lkddb.Browser.scan(self)
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.kerneldir)
            for subdir in self.dirs:
                for root, dirs, files in os.walk(subdir):
                    dirs.sort()
                    if old_kernel:
                        for kconf in fnmatch.filter(files, "Config.in"):
                            filename = os.path.join(root, kconf)
                            logger.debug("Config.in (<2.5) doing: " + filename)
                            self.__parse_config_in(filename)
                    else:
                        for kconf in fnmatch.filter(files, "Kconfig*"):
                            filename = os.path.join(root, kconf)
                            logger.debug("Kconfig (>=2.6) doing: " + filename)
                            self.__parse_kconfig(filename)
        finally:
            os.chdir(orig_cwd)

    def finalize(self):
        lkddb.Browser.finalize(self)

    def __parse_kconfig(self, filename):
        """read config menu in Kconfig"""
        f = open(filename, encoding='utf8', errors='replace')
        context = C_TOP
        config = None
        help = ""
        conf_type = None
        descr = ""
        depends = []
        for line in f:
            line = line.expandtabs()
            if context == C_HELP:
                ident_new = len(line) - len(line.lstrip())
                if ident < 0:
                    ident = ident_new
                if ident_new >= ident or line.strip() == "":
                    help += line.strip() + "\n"
                    continue
                context = C_CONF
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                continue
            try:
                tok, args = line.split(None, 1)
            except ValueError:
                tok, args = line, ""
            if tok in frozenset(("menu", "endmenu", "source", "if", "endif", "endchoice", "mainmenu")):
                if context == C_CONF:
                    self.__kconf_save(config, dict, conf_type, descr, depends, help, filename)
                context = C_TOP
                continue
            if tok in frozenset(("config", "menuconfig", "choice")):
                if context == C_CONF:
                    self.__kconf_save(config, dict, conf_type, descr, depends, help, filename)
                else:
                    context = C_CONF
                config = args
                help = ""
                dict = {}
                conf_type = None
                descr = ""
                depends = []
                continue
            if tok in frozenset(("help", "---help---")):
                if context != C_CONF:
                    help = ""
                    logger.error(
                        "kconfig: error: help out of context (%s), in %s, after '%s'" %
                        (context, filename, config))
                context = C_HELP
                ident = -1
                continue
            if tok in frozenset(("bool", "boolean", "tristate", "string", "hex", "int")):
                if tok == "boolean":
                    tok = "bool"
                conf_type = tok
                if not args or args[0] == "#":
                    descr = ""
                else:
                    div = args[0]
                    if not (div == '"' or div == "'"):
                        descr = args
                        logger.warning("kconfig: bad line in %s %s: '%s'" % (filename, config, line))
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
                            logger.warning("kconfig: bad line in %s %s: '%s': args=<%s>, s=%s" %
                                           (filename, config, line, args, s))
                            assert False
                        else:
                            d = s[2].split()
                            if len(d) > 1 and d[0] == "if":
                                depends.append(" ".join(d[1:]))
            if tok in frozenset(("default", "def_bool", "def_tristate")):
                if tok[3] == "_":
                    conf_type = tok[4:]
                    descr = ""
                if "#" in args:
                    args = args.split("#", 1)[0]
                s = args.split('if')
                if len(s) > 1:
                    d = s[1].split()
                    depends.append(" ".join(d))
            if tok == "prompt":
                div = args[0]
                assert div == '"' or div == "'"
                if div == '"':
                    args = args.replace('\\"', "'").replace("\\'", "'")
                    s = args.split(div)
                    descr = s[1]
                else:
                    args = args.replace('\\"', '"').replace("\\'", '"')
                    s = args.split(div)
                    descr = s[1].replace('"', "'")
                d = s[2].split()
                if len(d) > 1 and d[0] == "if":
                    depends.append(" ".join(d[1:]))
            if tok == "depends":
                if "#" in args:
                    args = args.split("#", 1)[0]
                d = args.split()
                if len(d) > 1 and d[0] == "on":
                    depends.append(" ".join(d[1:]))
                else:
                    # a missing "on"
                    depends.append(" ".join(d))
            if not context == C_CONF:
                # e.g. depents after "menu" or prompt and default after "choice"
                continue
            dict[tok] = args
        if context == C_CONF or context == C_HELP:
            self.__kconf_save(config, dict, conf_type, descr, depends, help, filename)

    def __parse_config_in(self, filename):
        # TODO
        raise NotImplementedError

    def __kconf_save(self, config, dict, conf_type, descr, depends, help, filename):
        if not conf_type:  # e.g. on 'choice'
            return
        config = "CONFIG_" + config
        if depends:
            if len(depends) > 1:
                depends = "(" + ")  &&  (".join(depends) + ")"
            else:
                depends = depends[0]
        else:
            depends = ""
        self.kconf_table.add_row((conf_type, descr, depends, help.strip(), config, filename))

        if conf_type == "tristate" or conf_type == "def_tristate":
            mod = self.makefiles.modules.get(config, None)
            if mod:
                if mod.find(" ") > -1:
                    logger.warning("warning: multiple modules in '%s': '%s" %
                                   (config, mod))
                for name in mod.split():
                    if not name.endswith(".o"):
                        if name[-1] == "/":
                            logger.error(
                                "Kconfig: name '%s' doesn't end with '.o (%s from %s)"
                                % (name, config, filename))
                        continue
                    self.module_table.add_row((name[:-2], descr, config, filename))
            else:
                logger.warning("kconfig: could not find the module obj of %s from %s" % (config, filename))
