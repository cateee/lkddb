#!/usr/bin/python
#:  utils.py : generic support for lkddb generator modules
#
#  Copyright (c) 2000,2001,2007  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details


import sys, re

_logfile = sys.stdout
_verbose = False

def log_init(verbose=1, logfile=sys.stdout):
    global _verbose, _logfile
    _verbose = verbose
    _logfile = logfile

def log(str):
    if _verbose:
        _logfile.write(str + "\n")

def log_extra(str):
    if _verbose > 1:
        _logfile.write(str + "\n")



# raw device list. format: -> scanner[class instance], data[scanner dependent], dep[set], filename[string]
devices = []

# device list in the final form (but unsorted)
db = []

def add_device(scanner, data, dep, filename):
    "add raw device data"
    devices.append((scanner, data, dep, filename))

def lkddb_add(string):
    "add a complete line to the lkddb"
    db.append("lkddb\t" + string + "\n") 

def lkddb_print(output_filename, header):
    "convert the raw data into full data and print it"
    for scanner, res, dep, filename in devices:
        dep = " ".join(dep)
	log_extra("# Checking device: %s, %s, %s # %s" %
	    (scanner.name, res, dep, filename))
	scanner.printer(res, dep, filename)
    db.sort()
    for i in xrange(len(db)-2, 0, -1):
        if db[i] == db[i+1]:
	    del db[i+1]
    f = open(output_filename, "w")
    f.write(header+"\n")
    f.writelines(db)
    f.close()

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
    def __init__(self, name, regex):
	self.name = name
	self.regex = re.compile(regex, re.DOTALL)
    def check(self):
	"check consistency"
	if self.splitter == None:
	    return False
        if self.printer == None:
	    return False
	return True
    def set_fields(self, field_list):
	"set field name of a device 'line'"
        self.fields = field_list
    def set_printer(self, printer):
        self.printer = printer

class scanner_array_of_struct(scanner):
    "an array of device structures"
    def __init__(self, name, struct_name):
	regex = r"\b%s\s+\w+\s*\w*\s*\[\d*\]\s*\w*\s*=\s*\{(.*?)\}\w*;" % struct_name
	scanner.__init__(self, name, regex)
	self.splitter = split_structs

class scanner_struct(scanner):
    "a single device structure"
    def __init__(self, name, struct_name):
        regex = r"\b%s\s+\w+\s*\w*\s*\w*\s*=\s*(\{.*?\})\w*;" % struct_name
        scanner.__init__(self, name, regex)
	self.splitter = split_structs

class scanner_funct(scanner):
    "a function call"
    def __init__(self, name, funct_name):
        regex = r"\b%s\s*\(([^()]*(?:\([^()]*\))?[^()]*(?:\([^()]*\))?[^()]*)\)" % funct_name
        scanner.__init__(self, name, regex)
        self.splitter = split_funct



scanners = []
def register_scanner(scanner):
    assert scanner.check() == True, "Not all field in scanner '%s' are set" % scanner.name
    scanners.append(scanner)


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
		log("input people smoke!, %s in '%s'" % (field, dictionary))
		return eval(val[val.find("=")+1:])
	    else:
		print "value():", field, dictionary
		print "'%s'" % val
		raise
	except NameError:
	    log("value error: expected number in field %s from %s" % (field, dictionary))
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
                log("str_value(): Numeric value of '%s'" % ret)
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


# ---------------------------------


field_init_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)\s*=\s*(.*)$", re.DOTALL)
subfield_re = re.compile(r"^\.([A-Za-z_][A-Za-z_0-9]*)(\.[A-Za-z_0-9]*\s*=\s*.*)$", re.DOTALL)

def parse_struct(scanner, fields, line, dep, filename, ret=False):
    "convert a struct (array of parameters) into a dictionary"
    #print "line--", filename, line
    res = {}
    nparam = 0
    for param in line:
        param = param.replace("\n", " ").strip()
        if not param:
            continue
        elif param[0] == ".":
	    m = field_init_re.match(param)
	    if m:
                field, value = m.groups()
	    else:
		m = subfield_re.match(param)
		if m:
		    field, value = m.groups()
		    value = "{" + value + "}"
		else:
                    print "parse_line(): ", filename, line, param
                    assert 0, "not expected syntax"
            res[field] = value
        else:
            try:
                res[fields[nparam]] = param
            except IndexError:
                print "Error: index error", table.name, fields, line, filename
                raise
        nparam += 1
    if res:
        if ret:
            return res
        # Maybe now we can call table.writer
        add_device(scanner, res, dep, filename)

