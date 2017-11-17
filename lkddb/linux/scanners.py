#!/usr/bin/python
#: lkddb/linux/scanners.py : scanners for Linux kernel
#
# Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
# This is free software, see GNU General Public License v2 (or later) for details

import re

import lkddb
import lkddb.log

__all__ = ("list_of_structs_scanner", "struct_scanner", "function_scanner",
           "split_funct", "split_structs",
           "extract_value", "extract_string", "extract_struct")


class struct_subscanner():

    def __init__(self, name, tree, parent_scanner, table_name):
        self.name = name
        self.tree = tree
        self.parent_scanner = parent_scanner
        self.table = self.tree.get_table(table_name)
        parent_scanner.register(self)
        self.raw = []

    def finalize(self):
        for data, filename, deps in self.raw:
            # we store also filename, to have useful error messages
            data['__filename'] = filename
            try:
                row = self.store(data)
            except:
                lkddb.log.exception("scanner<%s>.finalize: filename: %s, data: %s" % (
                                    self.name, filename, data))
                continue
            if row:
                self.table.add_row(row + (" ".join(sorted(deps)), filename))

    def store(self, data):
        # To be defined by children classes
        return ()


# ---------------

class list_of_structs_scanner(struct_subscanner):
    def __init__(self, name, tree, parent_scanner, struct_name, struct_fields, table_name):
        super().__init__(name=name, tree=tree, parent_scanner=parent_scanner, table_name=table_name)
        self.struct_name = struct_name
        self.struct_fields = struct_fields
        regex = r"\b%s\s+\w+\s*\w*\s*\[[^];]*\]\s*\w*\s*=\s*\{([^;]*)\}" % struct_name
        self.regex = re.compile(regex, re.DOTALL)
        self.splitter = split_structs


class struct_scanner(struct_subscanner):
    def __init__(self, name, tree, parent_scanner, struct_name, table_name, struct_fields):
        super().__init__(name=name, tree=tree, parent_scanner=parent_scanner, table_name=table_name)
        self.struct_name = struct_name
        self.struct_fields = struct_fields
        regex = r"\b%s\s+\w+\s*\w*\s*\w*\s*=\s*(\{.*?\})\w*;" % struct_name
        self.regex = re.compile(regex, re.DOTALL)
        self.splitter = split_structs


class function_scanner(struct_subscanner):
    def __init__(self, name, tree, parent_scanner, table_name, funct_name, funct_fields):
        super().__init__(name=name, tree=tree, parent_scanner=parent_scanner, table_name=table_name)
        self.struct_name = funct_name
        self.struct_fields = funct_fields
        regex = r"\b%s\s*\(([^()]*(?:\([^()]*\))?[^()]*(?:\([^()]*\))?[^()]*)\)" % funct_name
        self.regex = re.compile(regex, re.DOTALL)
        self.splitter = split_funct


###

def split_funct(block):
    return split_structs("{" + block + "}")


def split_structs(block):
    """from {a, b, c}, {d,e,f} ... to [[a,b,c], [d,e,f], ...]"""
    lines = []
    level = 0
    params = []
    sparam = 0
    in_str = False
    lbm = len(block)-1
    i = -1
    while i < lbm:
        i += 1
        c = block[i]
        if c == '"':
            in_str = not in_str
            continue
        if in_str:
            if c == '\\':
                i += 1
            continue
        if c == "{":
            level += 1
            if level == 1:
                sparam = i + 1
                params = []
        elif level == 1 and c == ",":
            params.append(block[sparam:i])
            sparam = i + 1
        elif c == "}":
            level -= 1
            if level == 0:
                params.append(block[sparam:i])
                lines.append(params[:])
    return lines


# --------------------

tri_re = re.compile(r"\(\s*\(([^)]+)\)\s*\?([^:]*):([^)]*)\)")
tri_re2 = re.compile(r"\(\s*([^()?]+)\?([^:]*):([^)]*)\)")
tri_re3 = re.compile(r"\s+([-0-9A-Za-z]+)\s*\?([^:]*):\s*\(([^)]*)\)")


def value_expand_tri(val):
    """expand  'b ? c : c' construct"""
    val = val.replace("(unsigned)", "")
    for r in (tri_re, tri_re2, tri_re3):
        m = r.search(val)
        while m is not None:
            cond, t, f = m.groups()
            try:
                if eval(cond):
                    if t:
                        res = t
                    else:
                        res = cond
                else:
                    res = f
            except:
                lkddb.log.log("error on value_expand_tri(val=%s): match: %s --- %s ---- %s" % (val, cond, t, f))
                assert False, "error on value_expand_tri(val=%s): match: %s --- %s ---- %s" % (val, cond, t, f)
            val = val[:m.start()] + res + val[m.end():]
            m = r.search(val)
    return eval(val)


def extract_value(field, dictionary):
    if field in dictionary:
        val = dictionary[field]
        if val[0] == "{" and val[-1] == "}":
            val = val[1:-1].strip()
        try:
            ret = eval(val)
        except SyntaxError:
            if val[-2:] == "UL" or val[-2:] == "ul":
                return eval(val[:-2])
            elif val.find("?") >= 0:
                return value_expand_tri(val)
            elif val.find("=") >= 0:
                lkddb.log.log("Hmmmm, %s in '%s'" % (field, dictionary))
                return eval(val[val.find("=")+1:])
            else:
                lkddb.log.log("error in extract_value: %s, %s --- '%s'" % (field, dictionary, val))
                assert False, "error in extract_value, 1: %s, %s --- '%s'" % (field, dictionary, val)
        except NameError:
            lkddb.log.log("error in extract_value: expected number in field %s from %s" %
                          (field, dictionary))
            return -1
        except:
            lkddb.log.log("error in extract_value, 2: %s, %s --- '%s'" % (field, dictionary, val))
            assert False, "error in extract_value, 1: %s, %s --- '%s'" % (field, dictionary, val)
        try:
            return int(ret)
        except ValueError:
            if len(ret) == 1:
                # ('X') --eval()--> X --> ord(X)
                return ord(ret)
            else:
                lkddb.log.log("str_value(): Numeric value of '%s'" % ret)
                assert False, "str_value(): Numeric value of '%s'" % ret
    else:
        return 0


char_cast_re = re.compile(r"\(\s*(const\s+)?char\s*\*\s*\)\s*", re.DOTALL)
null_pointer_re = re.compile(r"\(\s*void\s*\*\)\s*0", re.DOTALL)
field_init_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)$", re.DOTALL)
subfield_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)(\.[A-Za-z_0-9]*\s*=\s*.*)$", re.DOTALL)


def extract_string_rec(v, default=""):
    if v[0] == '(':
        if v[-1] == ')':
            return extract_string_rec(v[1:-1].strip(), default)
        else:
            if null_pointer_re.match(v):
                return default
            v = char_cast_re.sub("", v).strip()
            return extract_string_rec(v, default)
    if v[0] == '{' and v[-1] == '}':
        return extract_string_rec(v[1:-1].strip(), default)
    if v[0] == '"' and v[-1] == '"':
        return v[1:-1].replace("\t", " ")
    else:
        m = field_init_re.match(v)
        if m:
            field, value = m.groups()
            return extract_string_rec(value, default)
        lkddb.log.log("Error on assumptions in translating strings: value '%s'" % v)
        assert True
        return default


def extract_string(field, dictionary, default=""):
    if field in dictionary:
        v = dictionary[field]
        return extract_string_rec(v, default)
    else:
        return default


def extract_struct(field, dictionary, default=""):
    if field in dictionary:
        v = dictionary[field]
        if v[0] == '{' and v[-1] == '}':
            return v[1:-1].strip()
        lkddb.log.die("unknown structure format: %s" % v)
    else:
        return default
