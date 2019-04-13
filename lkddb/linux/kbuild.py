#!/usr/bin/python
#: lkddb/linux/kbuild.py : scanners for kernel build infrastructure
#
#  Copyright (c) 2000,2001,2007-2019  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import fnmatch
import logging
import os
import os.path
import re

import lkddb

logger = logging.getLogger(__name__)


# We can get configurations on building tools (what condition make
# a file to be compiled), and from configuration system (what
# precondition is needed to be able to see and select an option)
#
# But we have two varieties each: old and new:
# building: new kbuild and old "kmake"
# configuration: new Kconfig and old config.in


# kernel version and name

class Kver(lkddb.Browser):
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

# comment are removed; line ending with `\` are merged
kbuild_normalize = re.compile(
    r"(#.*$|\\\n)", re.MULTILINE)
kbuild_includes = re.compile(
    r"^-?include\s+\$[({]srctree[)}]/(.*)$", re.MULTILINE|re.ASCII)
kbuild_rules = re.compile(
    r"^([-A-Za-z0-9_]+)-([^-+=: \t\n]+)\s*[:+]?=[ \t]*(.*)$", re.MULTILINE|re.ASCII)

ignore_rules_set = frozenset(
    ("clean", "ccflags", "cflags", "aflags", "asflags", "mflags", "cpuflags", "subdir-ccflags", "extra"))


class Makefiles(lkddb.Browser):
    def __init__(self, firmware_table, kerneldir, dirs):
        super().__init__("kmake")
        self.firmware_table = firmware_table
        self.kerneldir = kerneldir
        self.dirs = dirs
        # dictionary of CONFIG_ dependencies for each file
        # dependencies: filename.c: {CONFIG_FOO, CONFIG_BAR, ...}
        self.dependencies = {}
        # dir_dep: dir: {CONFIG_FOO, ...}
        self.dir_dep = {}
        # dep_aliases: filename.c: (virtual-filename-objs.c, ...)
        self.dep_aliases = {}
        # modules: the inverse; format CONFIG_FOO: name  (used for module, so single name)
        self.modules = {}
        # pre parsed data
        # rules: filename: [[rule, dep, files] ...]  # rule-$(dep): files
        self.rules = {}
        # direct includes: filename -> [included file]
        self.includes = {}
        # variables: filename: [[variable_name, expansion],...]

    def scan(self):
        lkddb.Browser.scan(self)
        orig_cwd = os.getcwd()
        try:
            os.chdir(self.kerneldir)
            logger.info("=== Makefiles")
            for subdir in self.dirs:
                for root, dirs, files in os.walk(subdir):
                    dirs.sort()
                    if root.startswith('arch/') and subdir.count("/") == 1:
                        self.kbuild_parse_dir(root, 1)
                    else:
                        self.kbuild_parse_dir(root, 0)
        finally:
            os.chdir(orig_cwd)

    def kbuild_parse_dir(self, subdir, mode):
        # mode = 0: normal case -> path relatives; merge Kbuild and Makefile
        # mode = 1: arch/xxx/Makefile -> path from root
        # mode = 2: arch/xxx/Kbuild -> path relative, don't parse Makefile
        mk1 = os.path.normpath(os.path.join(subdir, "Makefile"))
        mk2 = os.path.normpath(os.path.join(subdir, "Kbuild"))
        mk1_exist = os.path.exists(mk1)
        mk2_exist = os.path.exists(mk2)
        if not mk1_exist and not mk2_exist:
            logger.warning("parse_kbuild: Makefile/Kbuild not found for dir %s" % subdir)
            return
        logger.debug("Reading Makefile/KBuild of " + subdir)
        if mode != 1 and mk2_exist:
            with open(mk2, encoding='utf8', errors='replace') as f:
                src = kbuild_normalize.sub(" ", f.read())
        else:
            src = ""
        if mode != 2 and mk1_exist:
            with open(mk1, encoding='utf8', errors='replace') as f:
                src += '\n' + kbuild_normalize.sub(" ", f.read())
        if not src:
            logger.warning("No Makefile/Kbuild in %s [mode=%s]" % (subdir, mode))
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
            # TODO: we do no care about order
            src = src[:m.start()] + "\n" + src2 + "\n" + src[m.end():]

        if mode == 1:
            # arch/*/Makefile is included from root Makefile
            # so paths are relative to root
            self.kbuild_parse_lines('', src)
            if mk2_exist:
                # we are in arch/*/Makefile and we should parse Kbuild but with
                # different context (subdir)
                self.kbuild_parse_dir(subdir, 2)
        else:
            self.kbuild_parse_lines(subdir, src)

    def kbuild_parse_alias(self, subdir, rule, prerequisites):
        if rule in {'obj', 'libs', 'init', 'drivers', 'net', 'core', 'virt', 'usr'}:
            return
        target = os.path.normpath(os.path.join(subdir, rule + ".c"))
        for this_pre_f in prerequisites.split():
            if this_pre_f[-2:] == ".o":
                this_pre_fn = os.path.normpath(os.path.join(subdir, this_pre_f))
                this_pre_fc = this_pre_fn[:-2] + ".c"
                self.dep_aliases.setdefault(this_pre_fc, []).append(target)

    def kbuild_parse_lines(self, subdir, src):
        subdir = os.path.normpath(subdir)
        path_comp = os.path.normpath(subdir).split('/')
        dir_deps = set()
        for i in range(len(path_comp)):
            parent_dir = '/'.join(path_comp[:i+1])
            dir_deps.update(self.dir_dep.get(parent_dir, set()))
        for (rule, dep, files) in kbuild_rules.findall(src):
            # rule-$(dep): file1 file2 dir1/ ...
            if not files or files.startswith('-'):  # compiler options
                continue
            if rule in ignore_rules_set:
                continue
            new_deps = dir_deps.copy()
            if dep in ("y", "m"):
                pass
            elif (dep[:9] == '$(CONFIG_' and dep[-1] == ')') or (
                  dep[:9] == '${CONFIG_' and dep[-1] == '}'):
                # obj-$(CONFIG_FOO_BAR) += file1.o file2.o subdir1/ ...
                i = dep.find(')', 10, -1)
                if i > 0:
                    if dep[i + 1:i + 10] == "$(CONFIG_":
                        # few cases with modname-$(CONFIG_A)$(CONFIG_B) += abc.o
                        new_deps.add(dep[2:i])
                        self.modules[dep[2:i]] = files
                        new_deps.add(dep[i + 3:-1])
                        self.modules[dep[i + 3:-1]] = files
                else:
                    new_deps.add(dep[2:-1])
                    if rule == "fw-shipped":
                        # obsolete rule, not used since 4.14
                        # should we handle also dep=y case?
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
                # this merge several files into a module, named {rule}
                self.kbuild_parse_alias(subdir, rule, files)
                continue
            else:
                logger.warning("parse_kbuild: unknown dep in %s: '%s'" % (subdir, dep))
                continue

            for f in files.split():
                if f[-2:] == ".o":
                    fn = os.path.normpath(os.path.join(subdir, f))
                    fc = fn[:-2] + ".c"
                    self.dependencies.setdefault(fc, set()).update(new_deps)
                elif f[-1] == "/":
                    new_dir = os.path.normpath(os.path.join(subdir, f))
                    if subdir:
                        self.dir_dep.setdefault(new_dir, set()).update(new_deps)
                    pass
                else:
                    logger.info("parse_kbuild: unknown target in '%s': '%s, was %s'" %
                                (subdir, f, (rule, dep, files)))

            self.kbuild_parse_alias(subdir, rule, files)

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


class Kconfigs(lkddb.Browser):
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
        old_kernel = self.tree.version_dict['numeric'] < (0x020500 + 45)
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
                            logger.debug("Config.in (<2.5.45) doing: " + filename)
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
        ident = 0
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
                    self.__kconf_save(config, conf_type, descr, depends, help, filename)
                context = C_TOP
                continue
            if tok in frozenset(("config", "menuconfig", "choice")):
                if context == C_CONF:
                    self.__kconf_save(config, conf_type, descr, depends, help, filename)
                else:
                    context = C_CONF
                config = args
                help = ""
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
        if context == C_CONF or context == C_HELP:
            self.__kconf_save(config, conf_type, descr, depends, help, filename)

    def __parse_config_in(self, filename):
        # TODO
        raise NotImplementedError

    def __kconf_save(self, config, conf_type, descr, depends, help, filename):
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
