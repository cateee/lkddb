#!/usr/bin/python
#:  devicetables.py : device tables template for source scanning and reporting
#
#  Copyright (c) 2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details


target = ('text', 'web', 'database') 

def get_row_fmt(fmt):
    ret = filter(None, map(lambda v: v[1], fmt))


# masks

def m8x(value):
    assert(value > -2  and  value < 2**(8))
    if value == -1:
	return ".."
    return "%02x" % value

def m16x(value):
    assert(value > -2  and  value < 2**(16))
    if value == -1:
        return "...."
    return "%04x" % value

def m24x(value):
    assert(value > -2  and  value < 2**(48))
    if value == -1:
        return "......"
    return "%06x" % value

def m32x(value):
    assert(value > -2  and  value < 2**(32))
    if value == -1:
        return "........"
    return "%08x" % value

def m64x(value):
    assert(value > -2  and  value < 2**(64))
    if value == -1:
        return "................"
    return "%016x" % value


# mask of mask

def mask_24m(v, m):
    ret = ""
    for i in range(24/4):
        if m[i] == "0":
            ret += "."
	# '~0' means 0xfffff for mask
        elif m[i] == "f" or m[i] == ".":
            ret += v[i]
        else:
            print "Unknow mask", v, m, len
            raise "KACerror"
    return ret

# simple

def special(value):
    return value

def str(value):
    return value

def qstr(value):
    return '"' + value + '"'


def int(value):
    return "%d" % value


# complex structures

def filename(value):
    return value

def deps(value):
    return value

