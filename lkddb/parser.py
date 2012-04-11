#!/usr/bin/python
#: lkddb/parser.py : this modules vaguely simulate a C preprocessor
#
# Copyright (c) 2007 by Giacomo A. Catenazzi <cate@cateee.net>
# This is free software, see GNU General Public License v2 (or later) for details
#

# It is not a good preprocessor, but it is enough for the
# most uses: Usually preprocessors hacks are done for code
# and not data.


# the file is divided in:
# - parse haders for #define
# - parse (detection) block, and expand macros


import re
import os.path
import lkddb
import lkddb.log
#import lkddb.linux.kbuild

#
#import lkddb_utils, kbuildparser, scanners


# global dictionaries

# filename -> set(filename..) of direct includes
includes_direct = {}
# filename -> frozenset(filename..) of includes (recursive)
includes_unwind = {}
# token -> [ filename -> expanded , .. ]
defines_pln = {}
# token -> [ filename -> (args, expanded) , .. ]
defines_fnc = {}
# string -> [ filename -> string , .. ]
defines_str = {}

# special cases:
print "with special includes"
includes_direct["drivers/char/synclink_gt.c"] = (
                set(["include/linux/synclink.h"]))
includes_unwind["drivers/char/synclink_gt.c"] = set([])

includes_direct["drivers/media/video/gspca/m5602/m5602_core.c"] = (
                 set(["include/linux/usb.h"]))
includes_unwind["drivers/media/video/gspca/m5602/m5602_core.c"] = set([])

includes_unwind["include/linux/compiler.h"] = set([])



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


def parse_header(src, filename, discard_source):
    "parse a single header file for #define, without recurse into other includes"
    src = comment_re.sub(" ", src)
    filename = os.path.normpath(filename)
    dir, ignore = filename.rsplit("/", 1)
    if not includes_direct.has_key(filename):
        includes_direct[filename] = set()
        includes_unwind[filename] = set([filename])
    for incl in include_re.findall(src):
        incl = incl.strip()
        if incl[0] == '"'  and  incl[-1] == '"':
            if not incl.endswith('.h"')  and not incl.endswith(".agh"):
                fn = os.path.join(dir, incl[1:-1])
                if not os.path.isfile(fn):
                    lkddb.log.log("preprocessor: parse_header(): unknow c-include in %s: %s" % (
                        filename, incl))
                    continue
                f = open(fn)
                src2 = f.read()
                f.close()
                src2 = src.replace(incl, "$"+incl[1:-1]+"$\n"+src2) 
                return parse_header(src2, filename, discard_source)
            else:
                includes_direct[filename].add(os.path.normpath(os.path.join(dir, incl[1:-1])))
        elif incl[0] == '<'  and  incl[-1] == '>':
            includes_direct[filename].add(os.path.normpath(os.path.join("include", incl[1:-1])))
        elif incl[0] == '$'  and  incl[-1] == '$':
            # it is a non .h recursive include (set called, from above
            continue
        else:
            lkddb.log.log("preprocessor: parse_header(): unknow include in %s: '%s'" % (
                filename, incl))
    for id, defs in define_re.findall(src):
        defines_pln.setdefault(id, {})
        defines_pln[id][filename] = defs.strip()
    for id, args, defs in define_fn_re.findall(src):
        defines_fnc.setdefault(id, {})
        defines_fnc[id][filename] = (args, defs.strip())
    if not discard_source:
        for id, defs in strings_re.findall(src):
            defines_str.setdefault(id, {})
            defines_str[id][filename] = defs.strip()
        return src

def unwind_include_rec(filename, known):
    incls = set([filename])
    if includes_direct.has_key(filename):
        incls.update(includes_direct[filename])
        known.update(includes_unwind[filename])
    for incl in incls.difference(known):
        known.add(incl)
        known.update(unwind_include_rec(incl, known))
    return known

def unwind_include(filename):
    known = set()
    res = unwind_include_rec(filename, known)
    includes_unwind[filename].update(res)

def unwind_include_all():
    for header in includes_direct.iterkeys():
        unwind_include(header)


def search_define(token, filename, defines):
    if not defines.has_key(token):
        return None
    defs = defines[token]
    for header in defs.iterkeys():
        if header == filename:
            return defs[header]
        if header in includes_unwind[filename]:
            return defs[header]
    return None

    
# ---------------


def expand_block(block, filename):
    ret = ""
    lbm = len(block)-1
    i = -1
    in_str = False
    start_token = -1
    while (i < lbm):
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
        if c.isalnum()  or  c == "_":
            if start_token < 0:
                start_token = i
        elif start_token >= 0:
            if block[start_token].isdigit():
                ret += expand_number(block[start_token:i])
            else:
                idx, ret_add = expand_token(block, start_token, i, filename)
                ret += ret_add
                if idx > i:
                    i = idx # the next char after token and parenthesis is already parsed
                    c = ""
            # now parse this character
            start_token = -1
            ret += c
        else:
            ret += c
    return ret


def expand_number(str):
    return str.rstrip("uUlL")


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
        while(i<pend):  
            i += 1              # end should be at last chat of token
            c = block[i]
            if c.isspace():
                continue
            elif c == '"'  and  pstart > 0:
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
            elif c == ","  and  level == 1:
                args.append(block[pstart:i].strip())
                pstart = i+1
        if pstart:
            return (pend, expand_macro(tok, df, args, filename) + " ")
    df = search_define(tok, filename, defines_pln)
    if df:
        return (0, expand_block(df+" ", filename) + " ")
    if block[start-1] == "."  or  block[start-2:start] == "->":
        # not in the right C namespace
        pass
    else:
        df = search_define(tok, filename, defines_str)
        if df:
            return (0, expand_block(df+" ", filename) + " ")
    return (0, tok)


concatenate_re = re.compile(r"\s*##\s*")

def expand_macro(tok, def_fnc, args, filename):
    def_args, defs = def_fnc
    defs = defs[:]
    def_args = def_args.split(",")
    if len(def_args) != len(args):
        # I don't think I'll ever parse debugging or "..." macros
        lkddb.log.log("Wrong lenghts: %s!=%s, %s, %s, %s, %s" % (len(def_args), len(args), def_args, args, tok, def_fnc))
        assert "WrongLen"
    
    for i in range(len(args)):
        da = def_args[i].strip()
        defs = re.sub(r"[^#]#" +da+ r"\b", '"'+args[i]+'"', defs)
        defs = re.sub(r"\b"    +da+ r"\b",     args[i],     defs)
    defs = concatenate_re.sub("", defs) + " "
    return expand_block(defs, filename)


