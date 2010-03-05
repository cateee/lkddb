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

import lkddb.log


# tasks
TASK_BUILD = 1       # scan and build lkddb
TASK_TABLE = 2       # read (and ev. format) tables
TASK_CONSOLIDATE = 3 # consolidate trees


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

_tree = None

def init(options):
    global _browsers, _scanners, _tables, _views
    lkddb.log.init(options)

#
# generic container to pass data between modules
#

def share(name, object):
    shared[name] = object

def set_working_tree(tree):
    global _tree
    _tree = tree
def get_working_tree():
    return _tree

#
# Generic classes for device_class and source_trees
#

class tree(object):
    def __init__(self, name):
        self.browsers = []
        self.scanners = []
        self.tables = {}
        self.views = []

        self.name = name
        self.version = None
	self.strversion = None
        self.ishead = None
        self.isreleased = None

    def save_versions(self):
	return (self.version, self.strversion, self.ishead, self.isreleased)
    def restore_versions(self, versions):
        self.version = versions[0]
        self.strversion = versions[1]
        self.ishead = versions[2]
        self.isreleased = versions[3]

    def get_version(self):
        return self.version
    def get_strversion(self):
	return self.strversion
    def is_released(self):
        return self.isreleased
    def is_head(self):
        return self.ishead
    def is_later(self, original_version):
        if self.ishead:
            return True
        if not self.isreleased:
            return False
        return (self.version > original_version)
    def is_older(self, original_version):
        if self.ishead or not self.isreleased:
            return False
        return (self.version < original_version)
    def check_version(self, vmin, vmax):
	if self.ishead:
	    if self.version >= vmax:
		return vmin, self.version
        if not self.isreleased:
	    return None, None
        if self.version > vmax:
	    return vmin, self.version
        if self.version < vmin:
            return self.version, vmin

    def register_browser(self, browser):
        self.browsers.append(browser)
    def register_scanner(self, scanner):
        self.scanners.append(scanner)
    def register_table(self, name, table):
        assert(name not in self.tables)
        self.tables[name] = table
    def get_table(self, name):
        return self.tables[name]

    def scan_sources(self):
        for s in self.browsers:
            s.scan()
    def finalize_sources(self):
        for s in self.browsers:
            s.finalize()

    def format_tables(self):
        for s in self.tables.itervalues():
            s.fmt()
    def prepare_sql(self, db, create=True):
        c = db.cursor()
        if create:
            create_generic_tables(c)
        for s in self.tables.itervalues():
            s.prepare_sql()
            if create:
              s.create_sql(c)
        db.commit()
        c.close()
    def write_sql(self, db):
        prepare_sql(db)
        for s in self.tables.itervalues():
            s.in_sql(db)

    #
    # persistent data:
    #   - data:  in python shelve format
    #   - lines: in text (line based) format
    #   - sql:   in SQL database
    #

    def write(self, data=None, list=None, sql=None):
        if data:
            self.write_data(data)
        if list:
            self.format_tables()
            self.write_list(list)
        if sql:
            db = sqlite3.connect(sql)
            self.write_sql(db)
            db.close()

    def write_data(self, filename, new=True):
        lkddb.log.phase("writing 'data'")
        if new:
            oflag = 'n'
        else:
            oflag = 'w'
        persistent_data = shelve.open(filename, flag=oflag)
	persistent_data['_versions'] = self.save_versions()
        for t in self.tables.itervalues():
            persistent_data[t.name] = t.rows
        persistent_data.sync()

    def read_data(self, filename, rw=False):
        lkddb.log.phase("reading 'data'")
        if rw:
                oflag = 'w'
        else:
                oflag = 'r'
        persistent_data = shelve.open(filename, flag=oflag)
        self.restore_versions(persistent_data['_versions'])
        for t in self.tables.itervalues():
            lkddb.log.log_extra("reading table " + t.name)
            rows = persistent_data.get(t.name, None)
            if rows != None:
                t.rows = rows
            t.restore()

    def consolidate_data(self, filename):
        lkddb.log.phase("reading 'data' to consolidate: %s" % filename)
        oflag = 'r'
        persistent_data = shelve.open(filename, flag=oflag)
        tree = persistent_data['_tree']
        version = self.get_version()
        for t in self.tables.itervalues():
            lkddb.log.log_extra("reading table " + t.name)
            rows = persistent_data.get(s.name, None)
            if rows != None:
                t.consolidate(tree, version, rows)

    def write_list(self, filename):
        lkddb.log.phase("writing 'list'")
        lines = []
        for t in self.tables.itervalues():
            new = t.get_lines()
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
        f.flush()
        f.close()


##########

class browser(object):
    def __init__(self, name):
        self.name = name
    def scan(self):
        lkddb.log.phase("browse and scan " + self.name)
    def finalize(self):
        lkddb.log.phase("finalizing scan " + self.name)

class scanner(object):
    def __init__(self, name):
        self.name = name

class table(object):
    def __init__(self, name):
        self.name = name
	self.rows = []
	self.fullrows = []
	self.consolidate = {}
	line_fmt = []
	for col_name, col_line_fmt, col_sql in self.cols:
	    if col_line_fmt:
		line_fmt.append(col_line_fmt)
	if line_fmt:
	    self.line_fmt = tuple(line_fmt)
	    self.line_templ = name + " %s"*len(line_fmt) + '\n'
    def add_fullrow(self, row):
	try:
	    r = []
	    for f, v in zip(self.line_fmt, row):
		r.append(f(v))
	    self.fullrows.append((row, tuple(r)))
	except AssertionError:
	    lkddb.log.log("assertion in table %s in fmt %s vith value %s [row:%s]" %
		(self.name, f, v, row) )
    def add_row(self, dict):
	self.rows.append(dict)
    def restore(self):
	pass
    def fmt(self):
	lkddb.log.phase("formatting " + self.name)
        for row in self.rows:
            self.add_fullrow(row)
    def get_lines(self):
	### TODO: change to an iteractor ########################
	lkddb.log.phase("printing lines in " + self.name)
	lines = []
	try:
	    for row, row_fmt, in self.full_rows:
	        lines.append(self.line_templ % row_fmt)
	except TypeError:
	    lkddb.log.exception("in %s, templ: '%s', row: %s" % (self.name, self.line_templ[:-1], row_fmt))
	return lines
    def consolidate(self, version, rows):
	lkddb.log.phase("consolidating lines in " + self.name)
        for row, row_fmt in self.fullrows:
	    vmin, vmax, orow = consolidate.get(v, (version, version, None))
	    if orow:
	        nmin, nmax = tree.check_version(vmin, vmax)
		if nmin != None:
		    consolidate[v] = (nmin, nmax, row)
	    else:
	        consolidate[v] = (vmin, vmax, orow)
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

