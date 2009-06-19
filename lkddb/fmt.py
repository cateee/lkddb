#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details



# masks

def fmt_m8x(value):
    assert(value > -2  and  value < 2**(8))
    if value == -1:
	return ".."
    return "%02x" % value

def fmt_m16x(value):
    assert(value > -2  and  value < 2**(16))
    if value == -1:
        return "...."
    return "%04x" % value

def fmt_m32x(value):
    assert(value > -2  and  value < 2**(32))
    if value == -1:
        return "........"
    return "%08x" % value

def fmt_m64x(value):
    assert(value > -2  and  value < 2**(64))
    if value == -1:
        return "................"
    return "%016x" % value


# mask of mask

def fmt_mask_32m(v, m):
    ret = ""
    for i in range(32/4):
        if m[i] == "0" or m[i] == ".":
            ret += "."
        elif m[i] == "f":
            ret += v[i]
        else:
            print "Unknow mask", v, m, len
            raise "KACerror"
    return ret

# simple

def fmt_pass(value):
    return value

def fmt_str(value):
    return value

def fmt_qstr(value):
    return '"' + value + '"'


def fmt_int(value):
    return "%d" % value


# complex structures

def fmt_filename(value):
    return value

def fmt_deps(value):
    return value

