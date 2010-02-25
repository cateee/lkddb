#!/usr/bin/python
#:  lkddb_utils.py : utilities for lkddb
#
#  Copyright (c) 2000,2001,2007-2009  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import sys
import traceback
import time
import shelve
import sqlite3

# global variables

# browse the files (of a source tree); select, open and preprocess files
_browsers = None
# scan a file content to find data (level of driver)
_scanners = None
# put devices in a standard form (level of hardware)
_tables = None
#
_views = None
#
_persistent_data = None
#
shared = {}
#
_verbose = 0
_logfile = sys.stdout
_phase = "(init)"
_start_time = 0


def init(verbose, logfile):
    global _browsers, _scanners, _tables, _views
    log_init(verbose, logfile)
    _browsers = []
    _scanners = []
    _tables = {}
    _views = []

#
# generic container to pass data between modules
#

def share(name, object):
    shared[name] = object

#
# Generic classes for device_class and source_trees
#

class browser(object):
    def __init__(self, name):
        self.name = name
    def scan(self):
        phase("browse and scan " + self.name)
    def finalize(self):
        phase("finalizing scan " + self.name)

class scanner(object):
    def __init__(self, name):
        self.name = name

class table(object):

    def __init__(self, name):
        self.name = name
	self.rows = []
	self.rows_fmt = []
	line_fmt = []
	for name, line, sql in self.cols:
	    if line:
		line_fmt.append(line)
	if line_fmt:
	    self.line_fmt = tuple(line_fmt)
	    self.line_templ = name + " %s"*len(line_fmt) + '\n'

    def add_row_fmt(self, row):
	try:
	    r = []
	    for f, v in zip(self.line_fmt, row):
		r.append(f(v))
	    self.rows_fmt.append(tuple(r))
	except AssertionError:
	    log("assertion in table %s in fmt %s vith value %s [row:%s]" %
		(self.name, f, v, row) )
    def add_row(self, dict):
	self.rows.append(dict)
    def restore(self):
	pass
    def fmt(self):
	phase("formatting " + self.name)
        for row in self.rows:
            self.add_row_fmt(row)
    def get_lines(self):
	### TODO: change to an iteractor ########################
	phase("printing lines in " + self.name)
	lines = []
	try:
	    for d in self.rows_fmt:
	        lines.append(self.line_templ % d)
	except TypeError:
	    print_exception("in %s, templ: '%s', row: %s" % (self.name, self.line_templ[:-1], d))
	return lines
    def prepare_sql(self, ver):
        sql_cols = []
        sql_create_col = []
	sql_insert_value = []
        for name, line, sql in self.cols:
            if sql:
		sql_cols.append(name)
		if sql[0] != '$':
                    sql_create_col.append(name + " " + sql)
		    sql_insert_value.append('?')
		else:
		    if sql.startswith("$kver"):
			sql_create_col.append(name + "INTEGER")
			sql_insert_value.append(str(self.ver))
		    elif sql == "$deps":
			sql_create_col.append(name + " FOREIGN KEY (") ###################
			sql_insert_value.append('?')
                    elif sql == "$config":
                        sql_create_col.append(name + " REFERENCES config(name)")
                        sql_insert_value.append('?')
                    elif sql == "$filename":
                        sql_create_col.append(name + " REFERENCES filename(name)")
                        sql_insert_value.append('?')
        if sql_cols:
            self.sql_create = ( "CREATE TABLE IF NOT EXISTS " + self.name + " (" +
		" id INTEGER PRIMARY KEY,\n" +
                ",\n ".join(sql_create_col) + " );" )
            self.sql_insert = ("INSERT OR UPDATE INTO " + self.name + " (" +
                ", ".join(sql_cols) + ") VALUES ("+
                ", ".join(("?",)*len(sql_cols)) + ");")

    def create_sql(self, cursor):
	cursor.execute(self.sql_create)
	sql = "INSERT OR IGNORE INTO `tables` (name) VALUES (" + self.name +");"
	cursor.execute(sql);
    def to_sql(self, db):
	c.cursor(db)
	for row in rows:
	    c.execute(self.sql_insert, row + self.extra_data)
	db.commit()
	c.close()

def create_generic_tables(c):
    sql = "CREATE TABLE IF NOT EXISTS `tables` (id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
    c.execute(sql);
    sql = "CREATE TABLE IF NOT EXISTS `filename` (id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
    c.execute(sql);
    sql = "CREATE TABLE IF NOT EXISTS `config` (id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
    c.execute(sql);
    sql = """CREATE TABLE IF NOT EXISTS `deps` (
 `config_id` INTEGER REFERENCE `config`,
 `item_id` INTEGER,
 `table_id` INTEGER REFERENCE `tables`
);"""
##################
	
#
# top level source and device scanners handling
#

def register_browser(browser):
    _browsers.append(browser)

def register_scanner(scanner):
    _scanners.append(scanner)

def register_table(name, table):
    assert(name not in _tables)
    _tables[name] = table

def get_table(name):
    return _tables[name]


def scan_sources():
    for s in _browsers:
	s.scan()

def finalize_sources():
    for s in _browsers:
	s.finalize()

def format_tables():
    for s in _tables.itervalues():
	s.fmt()

def prepare_sql(db, create=True):
    c = db.cursor()
    if create:
	create_generic_tables(c)
    for s in _tables.itervalues():
        s.prepare_sql()
	if create:
	  s.create_sql(c)  
    db.commit()
    c.close()

def write_sql(db):
    prepare_sql(db)
    for s in _tables.itervalues():
        s.in_sql(db)
 

#
# persistent data:
#   - data:  in python shelve format
#   - lines: in text (line based) format
#   - sql:   in SQL database
#

def write(data=None, list=None, sql=None):
    if data:
	write_data(data)
    if list:
	format_tables()
        write_list(list)
    if sql:
        db = sqlite3.connect(sql)
	write_sql(db)
	db.close()
#

def write_data(filename, new=True):
    phase("writing 'data'")
    if new:
        oflag = 'n'
    else:
        oflag = 'w'
    _persistent_data = shelve.open(filename, flag=oflag)
    for s in _tables.itervalues():
	_persistent_data[s.name] = s.rows
    _persistent_data.sync()

def read_data(filename, rw=False):
    phase("reading 'data'")
    if rw:
            oflag = 'w'
    else:
            oflag = 'r'
    _persistent_data = shelve.open(filename, flag=oflag)
    for s in _tables.itervalues():
	log_extra("reading device " + s.name)
	rows = _persistent_data.get(s.name, None)
	if rows != None:
	    s.rows = rows
	s.restore()

def write_list(filename):
    phase("writing 'list'")
    lines = []
    for s in _tables.itervalues():
	new = s.get_lines()
	lines.extend(new)
    lines.sort()
    lines2 = []
    old = None
    for l in lines:
	if l != old:
	    lines2.append(l)
	    old = l
    f = open(filename, "w")
    f.writelines(lines2)
    f.close()
	
#
# logs
#

def log_init(verbose=1, logfile=sys.stdout):
    global _verbose, _logfile, _start_time
    _verbose = verbose
    _logfile = logfile
    _start_time = time.time()

def elapsed_time():
    return (time.time() - _start_time)

def log(message):
    if _verbose:
        _logfile.write("*%3.1f: %s\n" % (elapsed_time(),  message))

def log_extra(message):
    if _verbose > 1:
	_logfile.write(".%3.1f: %s\n" % (elapsed_time(),  message))

def die(message, errorcode=1):
    _logfile.write("***%3.1f: fatal error: %s\n" % (elapsed_time(),  message))
    sys.stderr.write(message + "\n")
    sys.exit(errorcode=1)

def phase(phase):
    global _phase
    _phase = phase
    log_extra("PHASE:" + phase)

def print_exception(msg=None):
    _logfile.write("=" * 50 + "\nEXCEPTION in %s (after %.1f seconds)\n" %
			(_phase, elapsed_time()) )
    if msg:
        _logfile.write(msg + "\n")
	_logfile.write("-" * 10)
    traceback.print_exc(file=_logfile)
    _logfile.write("-" * 50 + "\n")
    _logfile.flush()

