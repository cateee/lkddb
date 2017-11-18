#!/usr/bin/python
#: fmt.py : utilities to format string and masks
#
#  Copyright (c) 2009-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import logging

import lkddb

logger = logging.getLogger(__name__)

target = ('text', 'web', 'database')


# masks

def m8x(value):
    assert(-2 < value < 2**8)
    if value == -1:
        return ".."
    return "%02x" % value


def m16x(value):
    assert(-2 < value < 2**16)
    if value == -1:
        return "...."
    return "%04x" % value


def m24x(value):
    assert(-2 < value < 2**48)
    if value == -1:
        return "......"
    return "%06x" % value


def m32x(value):
    assert(-2 < value < 2**32)
    if value == -1:
        return "........"
    return "%08x" % value


def m64x(value):
    assert(-2 < value < 2**64)
    if value == -1:
        return "................"
    return "%016x" % value


# mask of mask

def mask_24m(v, m):
    ret = ""
    for i in range(6):
        if m[i] == "0":
            ret += "."
        # '~0' means 0xfffff for mask
        elif m[i] == "f" or m[i] == ".":
            ret += v[i]
        else:
            raise lkddb.DataError("Unknow mask: v:%s, m:%s, len:%s" % (v, m, len))
    return ret


# simple

def special(value):
    return value


def str(value):
    return value


def qstr(value):
    return '"' + value + '"'


def dqstr(value):
    if value[0] == value[-1] and (value[0] == "'" or value[1] == '"'):
        return value[1:-1]
    else:
        return value


def int(value):
    return "%d" % value


# complex structures

def filename(value):
    return value


def deps(value):
    return value


def config_short(value):
    return "CONFIG_" + value
