#!/usr/bin/python
#: lkddb/parser.py : this modules vaguely simulate a C preprocessor
#
# Copyright (c) 2007-2017 by Giacomo A. Catenazzi <cate@cateee.net>
# This is free software, see GNU General Public License v2 (or later) for details
#

# It is not a good preprocessor, but it is enough for the
# most uses: Usually preprocessors hacks are done for code
# and not data.

# the file is divided in:
# - parse headers for #define
# - parse (detection) block, and expand macros

import re
import os.path
import logging

logger = logging.getLogger(__name__)

# global dictionaries

# -I directories (so used usually to look for <headers.h>
include_dirs = []
# {path, ...}
existing_headers = set()
parsed_files = set()

# filename -> set(filename..) of direct includes
direct_includes = {}
# filename -> set(filename..) of all includes (recursive)
all_dependencies = {}
# file name (without path) -> [ filename, .. ]
includes_file = {}
# token -> [ filename -> expanded , .. ]
defines_pln = {}
# token -> [ filename -> (args, expanded) , .. ]
defines_fnc = {}
# string -> [ filename -> string , .. ]
defines_str = {}

# Comments and join lines
comment_re = re.compile(
    r"(/\*.*?\*/|//.*?$|\\\n)", re.DOTALL | re.MULTILINE)
# Find #defines without arguments (ignore empty define: we don't care)
define_re = re.compile(r"^\s*#\s*define\s+([A-Za-z_0-9]+)[ \t]+(.+)$",
                       re.MULTILINE)
# Find #defines with arguments
define_fn_re = re.compile(r"^\s*#\s*define\s+([A-Za-z_0-9]+)\(([^)]*)\)[ \t]+(.+)$",
                          re.MULTILINE)
# includes directive
include_re = re.compile(r'^\s*#\s*include\s+(.*)$', re.MULTILINE)
# Find static strings
strings_re = re.compile(r'static\s+(?:const\s+)?char\s+(\w+)\s*\[\]\s*=\s*("[^"]*")\s*;', re.DOTALL)


def remember_file(filenames, path):
    for filename in sorted(filenames):
        full_path = os.path.normpath(os.path.join(path, filename))
        existing_headers.add(full_path)
        includes_file.setdefault(filename, []).append(full_path)


def parse_header(filename, return_source):
    """parse a single header file for #define, without recurse into other includes"""
    known_file = filename in parsed_files
    if known_file and not return_source:
        return
    f = open(filename, encoding='utf8', errors='replace')
    src = f.read()
    f.close()
    src = comment_re.sub(" ", src)
    filename = os.path.normpath(filename)
    if not known_file:
        path, ignore = filename.rsplit("/", 1)
        parsed_files.add(filename)
        if filename not in direct_includes:
            direct_includes.setdefault(filename, set())
        for incl in include_re.findall(src):
            incl = incl.strip()
            incl_name = incl[1:-1]
            if incl[0] == '"' and incl[-1] == '"':
                if not incl.endswith('.h"') and not incl.endswith('.agh"'):
                    fn = os.path.normpath(os.path.join(path, incl_name))
                    if not os.path.isfile(fn):
                        logger.warning("preprocessor: parse_header(): unknown c-include in %s: %s" % (
                            filename, incl))
                        continue
                    if os.path.samefile(filename, fn):
                        # kernel/locking/qspinlock.c includes himself
                        continue
                    direct_includes[filename].add(fn)
                    f = open(fn, encoding='utf8', errors='replace')
                    src2 = f.read()
                    f.close()
                    src = src.replace(incl, "\n" + src2)
                else:
                    # we try to find the local include without need to handle Makefile and -I flags
                    # 1- check if there is only one header with same name
                    base_filename = os.path.basename(incl_name)
                    headers = includes_file.get(base_filename, [])
                    if len(headers) == 1:
                        direct_includes[filename].add(headers[0])
                    else:
                        for i in range(3):
                            incl_path = os.path.normpath(os.path.join(path, ('../' * i) + incl_name))
                            if incl_path in existing_headers:
                                direct_includes[filename].add(incl_path)
                                break
                        else:
                            incl_filename = os.path.normpath(os.path.join(path, incl_name))
                            direct_includes[filename].add(incl_filename)
                            logger.warning('unknown include %s found in %s' % (incl, filename))
            elif incl[0] == '<' and incl[-1] == '>':
                base_filename = os.path.basename(incl_name)
                headers = includes_file.get(base_filename, [])
                if len(headers) == 1:
                    direct_includes[filename].add(headers[0])
                else:
                    for include_dir in include_dirs + [path]:
                        incl_path = os.path.normpath(os.path.join(include_dir, incl_name))
                        if incl_path in existing_headers:
                            direct_includes[filename].add(incl_path)
                            break
                    else:
                        direct_includes[filename].add(os.path.normpath(os.path.join("include", incl_name)))
            else:
                logger.warning("preprocessor: parse_header(): unknow include in %s: '%s'" % (
                    filename, incl))
        for name, defs in define_re.findall(src):
            defines_pln.setdefault(name, {})
            defines_pln[name][filename] = defs.strip()
        for name, args, defs in define_fn_re.findall(src):
            defines_fnc.setdefault(name, {})
            defines_fnc[name][filename] = (args, defs.strip())
    if return_source:
        for name, defs in strings_re.findall(src):
            defines_str.setdefault(name, {})
            defines_str[name][filename] = defs.strip()
        return src


def unwind_include(filename):
    if filename not in all_dependencies:
        all_dependencies[filename] = {filename}
        for header in direct_includes.get(filename, set()):
            all_dependencies[filename].update(unwind_include(header))
    return all_dependencies[filename]


def search_define(token, filename, defines):
    if token not in defines:
        return None
    defs = defines[token]
    headers = defs.keys()
    if filename in headers:
        return defs[filename]
    for header in headers:
        if header in all_dependencies[filename]:
            return defs[header]
    return None


# ---------------

def expand_block(block, filename):
    # we remove macro definitions
    block = define_fn_re.sub(" ", define_re.sub(" ", block))
    return _expand_block_in(block, filename)


def _expand_block_in(block, filename):
    ret = ""
    lbm = len(block)-1
    i = -1
    in_str = False
    start_token = -1
    while i < lbm:
        i += 1
        c = block[i]
        if c == '"':
            in_str = not in_str
            ret += c
            continue
        if in_str:
            if c == '\\':
                ret += block[i:i+2]
                i += 1
            else:
                ret += c
            continue
        if c.isalnum() or c == "_":
            if start_token < 0:
                start_token = i
        elif start_token >= 0:
            if block[start_token].isdigit():
                ret += expand_number(block[start_token:i])
            else:
                idx, ret_add = expand_token(block, start_token, i, filename)
                ret += ret_add
                if idx > i:
                    i = idx  # the next char after token and parenthesis is already parsed
                    c = ""
            # now parse this character
            start_token = -1
            ret += c
        else:
            ret += c
    return ret


def expand_number(text):
    return text.rstrip("uUlL")


def expand_token(block, start, end, filename):
    tok = block[start:end]
    df = search_define(tok, filename, defines_fnc)
    if df:
        pstart = 0
        pend = len(block)-1
        level = 0
        instr = False
        args = []
        i = end-1
        while i < pend:
            i += 1              # end should be at last chat of token
            c = block[i]
            if c.isspace():
                continue
            elif c == '"' and pstart > 0:
                instr = not instr
                continue
            elif instr:
                if c == '\\':
                    i += 1
                continue
            elif c == "(":
                if pstart == 0:
                    pstart = i+1
                level += 1
                continue
            elif pstart == 0:
                break
            elif c == ")":
                level -= 1
                if level == 0:
                    args.append(block[pstart:i].strip())
                    pend = i
                    break
                else:
                    continue
            elif c == "," and level == 1:
                args.append(block[pstart:i].strip())
                pstart = i+1
        if pstart:
            return pend, expand_macro(tok, df, args, filename) + " "
    df = search_define(tok, filename, defines_pln)
    if df:
        return 0, _expand_block_in(df+" ", filename) + " "
    if block[start-1] == "." or block[start-2:start] == "->":
        # not in the right C namespace
        pass
    else:
        df = search_define(tok, filename, defines_str)
        if df:
            return 0, _expand_block_in(df+" ", filename) + " "
    return 0, tok


concatenate_re = re.compile(r"\s*##\s*")


def expand_macro(tok, def_fnc, args, filename):
    def_args, defs = def_fnc
    defs = defs[:]
    def_args = def_args.split(",")
    if len(def_args) != len(args):
        # I don't think I'll ever parse debugging or "..." macros
        if def_args[-1].endswith("..."):
            # TODO: handle macro with args...
            pass
        else:
            logger.error("Wrong argument number in macro: %s!=%s, %s, %s, %s, %s in %s" % (
                len(def_args), len(args), def_args, args, tok, def_fnc, filename))
    else:
        for i in range(len(args)):
            da = def_args[i].strip()
            defs = re.sub(r"[^#]#" + da + r"\b", '"' + args[i] + '"', defs)
            defs = re.sub(r"\b"    + da + r"\b",       args[i],       defs)
    defs = concatenate_re.sub("", defs) + " "
    return _expand_block_in(defs, filename)
