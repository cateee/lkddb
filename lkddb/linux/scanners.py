#: lkddb/parser.py : hardware This modules vaguely simulate a C preprocessor
#
# It is not a good preprocessor, but it is enough for the
# most uses: Usually preprocessors hacks are done for code
# and not data.
#
# Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
# This is free software, distributed with the GPL version 2

import re

import lkddb
from lkddb.parser import unwind_include

__all__ = ("list_of_structs_scanner", "struct_scanner", "function_scanner",
	   "split_funct", "split_structs",
	   "extract_value", "extract_string", "nullstring_re")

class struct_subscanner(object):

    def __init__(self, name, parent_scanner, table_name):
	self.name = name
	self.parent_scanner = parent_scanner
	self.table = lkddb.get_table(table_name)
	parent_scanner.register(self)
	self.raw = []

    def finalize(self):
	self.data = []
        for data, filename, deps in self.raw:
            try:
                row = self.store(data)
            except:
                lkddb.print_exception(
                    "scanner<%s>.finalize: filename: %s, data: %s" % (
                    self.name, filename, data) )
                continue
	    if row:
                self.table.add_row(row + (filename, " ".join(sorted(deps))))

# ---------------

class list_of_structs_scanner(struct_subscanner):
    def __init__(self, name, parent_scanner, struct_name, struct_fields, table_name):
        struct_subscanner.__init__(self, name=name, parent_scanner=parent_scanner, table_name=table_name)
        self.struct_name = struct_name
        self.struct_fields = struct_fields
        regex = r"\b%s\s+\w+\s*\w*\s*\[[^];]*\]\s*\w*\s*=\s*\{(.*?)\}\s*;" % struct_name
        self.regex = re.compile(regex, re.DOTALL)
        self.splitter = split_structs

class struct_scanner(struct_subscanner):
    def __init__(self, name, parent_scanner, struct_name, table_name, struct_fields):
	struct_subscanner.__init__(self, name=name, parent_scanner=parent_scanner, table_name=table_name)
        self.struct_name = struct_name
        self.struct_fields = struct_fields
        regex = r"\b%s\s+\w+\s*\w*\s*\w*\s*=\s*(\{.*?\})\w*;" % struct_name
        self.regex = re.compile(regex, re.DOTALL)
        self.splitter = split_structs

class function_scanner(struct_subscanner):
    def __init__(self, name, parent_scanner, table, struct_name, struct_fields):
	struct_subscanner.__init__(self, name=name, parent_scanner=parent_scanner, table_name=table_name)
        self.struct_name = struct_name
        self.struct_fields = struct_fields
        regex = ( r"\b%s\s*\(([^()]*(?:\([^()]*\))?[^()]*(?:\([^()]*\))?[^()]*)\)"
			% funct_name )
        self.regex = re.compile(regex, re.DOTALL)
        self.splitter = split_funct


def split_funct(block):
    return split_structs("{" + block + "}")

def split_structs(block):
    "from {a, b, c}, {d,e,f} ... to [[a,b,c], [d,e,f], ...]"
    lines = []
    level = 0
    open = 0
    params = []
    sparam = 0
    in_str = False
    lbm = len(block)-1
    i = -1
    while (i < lbm):
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
                open = i+1
                sparam = i+1
                params = []
        elif level == 1  and  c == ",":
            params.append(block[sparam:i])
            sparam = i+1
        elif c == "}":
            level -= 1
            if level == 0:
                params.append(block[sparam:i])
                lines.append(params[:])
    return lines



# Unwind some arrays (i.e. in pcmcia_device_id):
unwind_array = ("n0", "n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9")

# --------------------

nullstring_re = re.compile(r"\([ \t]*void[ \t]*\*[ \t]*\)[ \t]*0")

tri_re  = re.compile(r"\(\s*\(([^\)]+)\)\s*\?([^:]*):([^\)]*)\)")
tri_re2 = re.compile(r"\(\s*([^\(\)\?]+)\?([^:]*):([^\)]*)\)")
tri_re3 = re.compile(r"\s+([-0-9A-Za-z]+)\s*\?([^:]*):\s*\(([^\)]*)\)")

def value_expand_tri(val):
    "expand  'b ? c : c' construct"
    val = val.replace("(unsigned)", "")
    for r in (tri_re, tri_re2, tri_re3):
        m = r.search(val)
        while ( m != None):
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
                print "val:", val
                print "match:", cond, "---", t, "----", f
                raise
            val = val[:m.start()] + res + val[m.end():]
            m = r.search(val)
    return eval(val)
    
def extract_value(field, dictionary):
    if dictionary.has_key(field):
        val = dictionary[field]
        if val[0] == "{"  and  val[-1] == "}":
            val = val[1:-1].strip()
        try:
            ret = eval(val)
        except SyntaxError:
            if val[-2:] == "UL" or  val[-2:] == "ul":
                return eval(val[:-2])
            elif val.find("?") >=0:
                return value_expand_tri(val)
            elif val.find("=") >=0:
                lkddb.log("Hmmmm, %s in '%s'" % (field, dictionary))
                return eval(val[val.find("=")+1:])
            else:
                print "value():", field, dictionary
                print "'%s'" % val
                raise
        except NameError:
            lkddb.log("value error: expected number in field %s from %s"
			% (field, dictionary))
            return -1
        except:
            print "eval error", field, val, dictionary
            raise

        try:
            return int(ret)
        except ValueError:
            if len(ret) == 1:
                # ('X') --eval()--> X --> ord(X)
                return ord(ret)
            else:
                lkddb.log("str_value(): Numeric value of '%s'" % ret)
                raise
    else:
        return 0

def mask_value(val, any, deep):
    "convert numeric 'val' in a string.  If 'any', then write the mask" 
    ret = "." * deep
    if any < 0  and  val < 0:
        return ret
    elif val == any:
        return ret
    form = "%%%u.%ux" % (deep, deep)
    try:
        ret = form % val
    except TypeError:
        if val[0] == "'"  and  val[2] == "'"  and  len(val) == 3:
            ret = form % ord(val[1])
    return ret


def mask_mask(v, m, len=6):
    ret = ""
    for i in range(len):
        if m[i] == "0":
            ret += "."
        elif m[i] == "f":
            ret += v[i]
        else:
            print "Unknow mask", v, m, len
            raise "KACerror"
    return ret

def chars(field, dictionary, lenght=4, default="...."):
    if dictionary.has_key(field):
        v = dictionary[field]
        l = len(v)
        if l == 2:
            return default
        if v[0] == '"'  and  v[-1] == '"'  and  len(v) == lenght+2:
            return v[1:-1]
        else:
            print "Error on assumptions in translating chars:", field, dictionary, lenght, default, v
            raise "KACerror"
    else:
        return default

char_cast_re = re.compile(r"\(\s*char\s*\*\s*\)\s*", re.DOTALL)
field_init_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)$", re.DOTALL)
subfield_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)(\.[A-Za-z_0-9]*\s*=\s*.*)$", re.DOTALL)

def extract_string(field, dictionary, default=""):
    if dictionary.has_key(field):
        v = dictionary[field]
        if v[0] == '(':
            if v[-1] == ')':
                v = v[1:-1].strip()
            else:
                v = char_cast_re.sub("", v).strip()
        if v[0] == '{'  and  v[-1] == '}':
            v = v[1:-1].strip()
        if v[0] == '"'  and  v[-1] == '"':
            return v.replace("\t", " ")
        else:
            m = field_init_re.match(v)
            if m:
                field, value = m.groups()
                return strings("recursive", {"recursive": value}, default)
            m = char_cast_re.search(v)

            print "Error on assumptions in translating strings:", field, dictionary, default, v
            return default
    else:
        return default

