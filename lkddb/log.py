#!/usr/bin/python
#: lkddb/log.py : log utilities for lkddb
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import sys
import traceback
import time

_verbose = 0
_logfile = None
_phase = "(init)"
_start_time = 0
_timed_logs = False


def _get_versioned_name(log_filename, version):
    i = log_filename.find("%")
    if i == -1:
        return log_filename
    size = len(log_filename)
    vsize = len(version)
    while(i >= 0):
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
    global _verbose, _timed_logs, _logfile, _start_time
    _verbose = options.verbose
    _timed_logs = options.timed_logs
    log_filename = options.log_filename
    if log_filename == None  or  log_filename == "-":
        _logfile = sys.stdout
    else:
        if options.versioned:
            log_filename = _get_versioned_name(log_filename, options.version)
        if _logfile != None:
            _logfile.flush()
            _logfile.close()
        _logfile = open(log_filename, 'w')
    _start_time = time.time()
    _logfile.flush()

def finalize():
    if _logfile != None:
        _logfile.flush()
        _logfile.close()

def elapsed_time():
    return (time.time() - _start_time)


def log(message):
    if _verbose:
        if _timed_logs:
            _logfile.write("*%3.1f: %s\n" % (elapsed_time(),  message))
        else:
            _logfile.write("* %s\n" % message)
        _logfile.flush()

def log_extra(message):
    if _verbose > 1:
        if _timed_logs:
            _logfile.write(".%3.1f: %s\n" % (elapsed_time(),  message))
        else:
            _logfile.write(". %s\n" % message)
        _logfile.flush()

def die(message, errorcode=1):
    sys.stdout.flush()
    sys.stderr.flush()
    _logfile.write("***%3.1f: fatal error: %s\n" % (elapsed_time(),  message))
    _logfile.flush()
    sys.stderr.write(message + "\n")
    sys.stderr.flush()
    sys.exit(1)

def phase(phase):
    global _phase
    _phase = phase
    log_extra("PHASE:" + phase)

def exception(msg=None):
    sys.stdout.flush()
    sys.stderr.flush()
    _logfile.write("=" * 50 + "\nEXCEPTION in %s (after %.1f seconds)\n" %
                        (_phase, elapsed_time()) )
    if msg:
        _logfile.write(msg + "\n")
        _logfile.write("-" * 10)
    traceback.print_exc(file=_logfile)
    _logfile.write("-" * 50 + "\n")
    _logfile.flush()


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

