#!/usr/bin/python
#: scanners.py : scanners classes and utilities for lkddb
#
#  Copyright (c) 2000,2001,2007,2008  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import re
import utils

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


class scanner:
    "container of scanner data and procedures"
    delay_init = True
    def __init__(self, name, format, db_attrs, regex, struct_fields):
	self.name = name
	self.format = format
	self.db_attrs = db_attrs
	self.regex = re.compile(regex, re.DOTALL)
	self.struct_fields = struct_fields
	self.slitter = None
	if not scanner.delay_init:
	    self.scanner_id = utils.new_scanner_table(name, format, db_attrs)
	self.select_id = ("SELECT "+name+"_id FROM "+name+"s " +
		"WHERE " +   "=? AND ".join(db_attrs) + "=?;")
	self.insert_id = ("INSERT INTO "+name+"s (" +
	    ", ".join(db_attrs) + ") VALUES ("+
	    ("?,"*len(db_attrs))[:-1] + ");")


class scanner_array_of_struct(scanner):
    "an array of device structures"
    def __init__(self, name, format, db_attrs, struct_name, struct_fields):
	regex = r"\b%s\s+\w+\s*\w*\s*\[[^];]*\]\s*\w*\s*=\s*\{(.*?)\}\s*;" % struct_name
	scanner.__init__(self, name, format, db_attrs, regex, struct_fields)
	self.splitter = split_structs

class scanner_struct(scanner):
    "a single device structure"
    def __init__(self, name, format, db_attrs, struct_name, struct_fields):
        regex = r"\b%s\s+\w+\s*\w*\s*\w*\s*=\s*(\{.*?\})\w*;" % struct_name
        scanner.__init__(self, name, format, db_attrs, regex, struct_fields)
	self.splitter = split_structs

class scanner_funct(scanner):
    "a function call"
    def __init__(self, name, format, db_attrs, funct_name, funct_args):
        regex = r"\b%s\s*\(([^()]*(?:\([^()]*\))?[^()]*(?:\([^()]*\))?[^()]*)\)" % funct_name
        scanner.__init__(self, name, format, db_attrs, regex, funct_args)
        self.splitter = split_funct



active_scanners = []
other_scanners  = []
def register_scanner(scanner, type=active_scanners):
    type.append(scanner)

def scanner_init():
    for s in active_scanners:
	s.scanner_id = utils.new_scanner_table(s.name, s.format, s.db_attrs)
        scanner.delay_init = False
    for s in other_scanners:
        s.scanner_id = utils.new_scanner_table(s.name, s.format, s.db_attrs)


# Unwind some arrays (i.e. in pcmcia_device_id):
unwind_array = ("n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9")

# --------------------

nullstring_re = re.compile(r"\([ \t]*void[ \t]*\*[ \t]*\)[ \t]*0")

tri_re  = re.compile(r"\(\s*\(([^\)]+)\)\s*\?([^:]*):([^\)]*)\)")
tri_re2 = re.compile(r"\(\s*([^\(\)\?]+)\?([^:]*):([^\)]*)\)")
tri_re3 = re.compile(r"\s+([-0-9A-Za-z]+)\s*\?([^:]*):\s*\(([^\)]*)\)")

def value_expand_tri(val):
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
    

def value(field, dictionary):
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
		utils.log("Hmmmm, %s in '%s'" % (field, dictionary))
		return eval(val[val.find("=")+1:])
	    else:
		print "value():", field, dictionary
		print "'%s'" % val
		raise
	except NameError:
	    utils.log("value error: expected number in field %s from %s" % (field, dictionary))
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
                utils.log("str_value(): Numeric value of '%s'" % ret)
                raise
    else:
        return 0

def str_value(val, any, deep):
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


def mask(v, m, len=6):
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

def strings(field, dictionary, default='""'):
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


