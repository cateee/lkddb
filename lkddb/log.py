#!/usr/bin/python
#: lkddb/log.py : log utilities for lkddb
#
#  Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import logging


def _get_versioned_name(log_filename, version):
    i = log_filename.find("%")
    if i == -1:
        return log_filename
    size = len(log_filename)
    vsize = len(version)
    while i >= 0:
        i = log_filename.find("%", i)
        if i == -1:
            return log_filename
        if i >= size - 1:  # last char
            return log_filename[:i] + version
        else:
            if log_filename[i+1] == "%":
                log_filename = log_filename[:i] + log_filename[i+1:]
                i += 1
                size -= 1
            else:
                log_filename = log_filename[:i] + version + log_filename[i+1:]
                size += vsize
    return log_filename


def init(options):
    level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG
    }.get(options.verbose, logging.DEBUG)
    log_filename = options.log_filename
    if log_filename is None or log_filename == "-":
        logging.basicConfig(level=level)
    else:
        try:
            if options.versioned:
                log_filename = _get_versioned_name(log_filename, options.version)
        except AttributeError:
            pass
        logging.basicConfig(filename=log_filename, filemode='w', level=level)


if __name__ == "__main__":
    v = "1.2.3"
    assert _get_versioned_name("logfile", v) == "logfile"
    assert _get_versioned_name("", v) == ""
    assert _get_versioned_name("%.log", v) == "1.2.3.log"
    assert _get_versioned_name("%%.log", v) == "%.log"
    assert _get_versioned_name("%", v) == "1.2.3"
    assert _get_versioned_name("%%", v) == "%"
    assert _get_versioned_name("lkddb-%.log", v) == "lkddb-1.2.3.log"
    assert _get_versioned_name("lkddb-%%.log", v) == "lkddb-%.log"
    assert _get_versioned_name("lkddb-%.%.log", v) == "lkddb-1.2.3.1.2.3.log"
    assert _get_versioned_name("lkddb%%-%.log", v) == "lkddb%-1.2.3.log"
    assert _get_versioned_name("lkddb-%.%%log", v) == "lkddb-1.2.3.%log"
