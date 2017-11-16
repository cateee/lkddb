#!/usr/bin/python
#: lkddb/__init__.py : generic definitions (and classes) for lkddb
#
#  Copyright (c) 2000,2001,2007-2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import sys
import os.path
import traceback
import time
import shelve
import sqlite3

import lkddb.log

# tasks
TASK_BUILD = 1       # scan and build lkddb
TASK_TABLE = 2       # read (and ev. format) tables
TASK_CONSOLIDATE = 3 # consolidate trees (with versions)


def init(options):
    lkddb.log.init(options)

#
# Generic container to pass global data between modules
#

def share(name, object):
    shared[name] = object

#
# Generic classes for device_class and source_trees
#

class storage(object):
    "container of trees (for persistent_data)"

    def __init__(self):
        self.available_trees = {}   # treename -> tree
        self.available_tables = {}  # tablename -> (treename, table)
        self.readed_trees = {}	    # treename -> tree

    def register_tree(self, tree):
        self.available_trees[tree.name] = tree
        for tabname, tab in tree.tables.iteritems():
            self.available_tables[tabname] = (tree.name, tab)

    def read_consolidate(self, filename):
        lkddb.log.phase("reading data-file to consolidate: %s" % filename)
        if not os.path.exists(filename):
            lkddb.log.die("file '%s' don't exist" % filename)
        persistent_data = shelve.open(filename, flag='r')
        try:
            trees = persistent_data['_trees']
            tables = persistent_data['_tables']
        except KeyError:
            lkddb.log.die("invalid data in file '%s'" % filename)
        consolidated = persistent_data.get('_consolidated', False)
        for treename in trees:
            lkddb.log.log_extra("consolidating tree '%s'" % treename)
            tree = self.available_trees[treename]
            tree.read_consolidate(consolidated, persistent_data)
            self.readed_trees.update(map(lambda name: (name, self.available_trees[name]), trees))
        persistent_data.close()

    def write_consolidate(self, filename, new=True):
        lkddb.log.phase("writing consolidate data '%s'" % filename)
        if new:
            oflag = 'n'
        else:
            oflag = 'w'
        persistent_data = shelve.open(filename, flag=oflag)
        trees = []
        tables = []
        versions = set(())
        for tree in self.readed_trees.values():
            lkddb.log.phase("writing consolidated tree '%s'" % tree.name)
            new_persistent = tree.write_consolidate()
            new_tables = new_persistent['_tables']
            trees.append(tree.name)
            tables.extend(new_tables)
            versions.update(new_persistent['_versions'])
            for t in new_tables:
                if t in persistent_data:
                    lkddb.log.die("two different trees share the table name '%s'" % t)
                persistent_data[t] = new_persistent[t]
        persistent_data['_trees'] = trees
        persistent_data['_tables'] = tables
        persistent_data['_versions'] = versions
        persistent_data['_consolidated'] = True

        persistent_data.sync()
        persistent_data.close()


class tree(object):
    "defines sources of a project with task, a base path, a version and some related browsers"
    # e.g. kernel sources

    def __init__(self, name):
        self.name = name

        self.browsers = []
        self.scanners = []
        self.tables = {}
        self.views = []

        #self.version = [ "tree", (num_version), "strversion", series ]
        #self_consolidated_versions = set((self.version))
        self.version = None
        self.consolidated_versions = set(())

    def get_strversion(self):
        if self.version == None:
            self.retrive_version()
        return self.version[2]
    def retrive_version(self):
        pass

    def register_browser(self, browser):
        self.browsers.append(browser)
    def register_scanner(self, scanner):
        self.scanners.append(scanner)
    def register_table(self, name, table):
        assert name not in self.tables, "table '%s' already registered'" % name
        self.tables[name] = table
    def get_table(self, name):
        return self.tables[name]

    def scan_sources(self):
        for b in self.browsers:
            b.scan()
    def finalize_sources(self):
        for b in self.browsers:
            b.finalize()

    def format_tables(self):
        for t in self.tables.values():
            t.fmt()
    def prepare_sql(self, db, create=True):
        c = db.cursor()
        if create:
            create_generic_tables(c)
        for t in self.tables.values():
            t.prepare_sql()
            if create:
              t.create_sql(c)
        db.commit()
        c.close()
    def write_sql(self, db):
        prepare_sql(db)
        for t in self.tables.values():
            t.in_sql(db)

    #
    # persistent data:
    #   - data:  in python shelve format  [rows (raw)]
    #   - lines: in text (line based) format [fullrows (sort+uniq)]
    #   - sql:   in SQL database
    #   - consolidate: in python shelve format [crows (with all versions)]
    #

    def write(self, data_filename=None, list_filename=None, sql_filename=None):
        if data_filename:
            self.write_data(data_filename)
        if list_filename:
            self.format_tables()
            self.write_list(list_filename)
        if sql_filename:
            self.write_sql(sql_filename)

    def write_data(self, filename, new=True):
        lkddb.log.phase("writing 'data'")
        if new:
            oflag = 'n'
        else:
            oflag = 'w'
        persistent_data = shelve.open(filename, flag=oflag)
        persistent_data['_version'] = self.version
        persistent_data['_tables'] = tuple(self.tables.keys())
        persistent_data['_trees'] = [self.name]
        for t in self.tables.values():
            persistent_data[t.name] = t.rows
        persistent_data.sync()
        persistent_data.close()

    def read_data(self, filename):
        lkddb.log.phase("reading data-file: '%s'" % filename)
        if os.path.isfile(filename):
            persistent_data = shelve.open(filename, flag='r')
            try:
                tables = persistent_data['_tables']
                trees = persistent_data['_trees']
                self.version = persistent_data['_version']
            except KeyError:
                lkddb.log.die("invalid data in file '%s'" % filename)
            if self.name not in trees:
                lkddb.log.die("file '%s' is not a valid data file for tree %s" % (filename, self.name))
            for t in self.tables.values():
                if t.name not in tables:
                    lkddb.log.log_extra("table '%s' not found in '%s'" % (t.name, filename))
                    continue
                lkddb.log.log_extra("reading table '%s'" % t.name)
                rows = persistent_data.get(t.name, None)
                if rows != None:
                    t.rows = rows
                    t.restore()
            persistent_data.close()
        else:
            lkddb.log.die("could not read file '%s' % filename")

    def read_consolidate(self, consolidated, persistent_data):
        if not consolidated:
            ver = persistent_data['_version']
            self.consolidated_versions.add(ver)
        else:
            ver = None
            self.consolidated_versions.update(persistent_data['_versions'])
        for t in self.tables.values():
            lkddb.log.log_extra("reading table '%s'" % t.name)
            rows = persistent_data.get(t.name, None)
            if rows != None:
                if not consolidated:
                    t.rows = rows
                    t.restore()
                    t.fmt()
                else:
                    t.crows_tmp = rows
                t.consolidate_table(consolidated, ver)
                if consolidated:
                    del t.crows_tmp
            else:
                lkddb.log.log_extra("table '%s' is empty" % t.name)
                if not hasattr(self, 'crows'):
                    self.crows = {}


    def write_consolidate(self):
        persistent_data = {}
        persistent_data['_tables'] = tuple(self.tables.keys())
        persistent_data['_versions'] = self.consolidated_versions
        for t in self.tables.values():
            persistent_data[t.name] = t.crows
        return persistent_data

    def append_data(self, filename, table_list):
        "append new tables to an existing consolidated data file"
        assert False, "remove this function"
        persistent_data = shelve.open(filename, flag='w')
        consolidated = persistent_data['_consolidated']
        tables = persistent_data['_tables']
        for t in table_list:
            if not t.name in tables:
                tables += (t.name,)
            persistent_data[t.name] = t.crows
        persistent_data['_tables'] = tables
        persistent_data.sync()
        persistent_data.close()

    def write_list(self, filename):
        lkddb.log.phase("writing 'list'")
        lines = []
        for t in self.tables.values():
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

    def write_sql(self, filename):
        lkddb.log.phase("writing 'sql'")
        ver = self.version
        db = sqlite3.connect(filename)
        c = db.cursor()
        lfddb = lkddb.create_generic_tables(c)
        for t in self.tables.values():
            t.prepare_sql(ver)
            t.create_sql(c)
        db.commit()
        c.close()
        for t in self.tables.values():
            t.to_sql(db)
        db.commit()
        db.close()


class browser(object):
    "scan a tree. In two phases: 'scan' read the tree; 'finalize' do the rest"
    # two phases: only after reading all sources, we can do cross-references

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
        line_indices = []
        for col_index, col_name, col_line_fmt, col_sql in self.cols:
            if col_line_fmt:
                line_indices.append(col_index)
                line_fmt.append(col_line_fmt)
        self.line_fmt = tuple(line_fmt)
        self.line_len = len(line_fmt)
        self.col_len = len(self.cols)
        self.key1_len = len([v for v in line_indices if v>0])
        self.key2_len = len([v for v in line_indices if -10<v<0])
        self.values_len = len([v for v in line_indices if v==0])
        assert self.line_len == (self.key1_len + self.key2_len + self.values_len)

        indices = [0] * self.line_len
        indices_inv = [0] * self.line_len
        i_val = self.key1_len
        for i in range(self.line_len):
            idx = line_indices[i]
            if idx > 0:
                indices[i] = idx-1
                indices_inv[idx-1] = i
            elif -10 < idx < 0:
                indices[i] = self.key1_len + self.values_len + abs(idx)-1
                indices_inv[self.key1_len + self.values_len + abs(idx)-1] = i
            elif idx == 0:
                indices[i] = i_val
                indices_inv[i_val] = i
                i_val += 1
            else:
                assert False, "unkown code of index"
        self.indices = tuple(indices)
        self.indices_inv = tuple(indices_inv)
        if line_fmt:
            self.line_templ = name + ( " %s" * self.key1_len + " %s" * self.values_len + " : %s" * self.key2_len +'\n')

    def add_fullrow(self, row):
        # format data
        r = []
        try:
            for f, v in zip(self.line_fmt, self.pre_row_fmt(row)):
                r.append(f(v))
        except AssertionError:
            lkddb.log.log("assertion in table %s in row %s" %
                (self.name, row) )
            return
        # order data
        rr = tuple(map(lambda i: r[self.indices_inv[i]], range(self.line_len)))
        self.fullrows.append(tuple(rr))
    def pre_row_fmt(self, row):
        return row
    def add_row(self, row):
        self.rows.append(row)
    def restore(self):
        self.fullrows = []
        pass
    def fmt(self):
        if not self.line_fmt:
            return
        lkddb.log.phase("formatting " + self.name)
        for row in self.rows:
            self.add_fullrow(row)
    def get_lines(self):
        ### TODO: change to an iteractor ########################
        lkddb.log.phase("printing lines in " + self.name)
        lines = []
        try:
            for fullrow in self.fullrows:
                lines.append(self.line_templ % fullrow)
        except TypeError:
            lkddb.log.exception("in %s, templ: '%s', row: %s" % (self.name, self.line_templ[:-1], row_fmt))
        return lines

    def consolidate_table(self, consolidated, ver):
        lkddb.log.phase("consolidating lines in " + self.name)
        if not hasattr(self, 'crows'):
            self.crows = {}

        # consolitating
        if consolidated:
            for key1, values1 in self.crows_tmp.iteritems():
                for key2, values2 in values1.iteritems():
                    values, all_versions = values2
                    actual_crow = self.crows.get(key1, None)
                    if actual_crow == None:
                        self.crows[key1] = {key2: [values, all_versions]}
                    else:
                        actual_sub_crow = actual_crow.get(key2, None)
                        if actual_sub_crow == None:
                            self.crows[key1][key2] = [values, all_versions]
                        else:
                            self.crows[key1][key2][0] = values
                            self.crows[key1][key2][1].update(all_versions)
        else:
            for fullrow in self.fullrows:
                key1 = fullrow[:self.key1_len]
                key2 = fullrow[self.key1_len+self.values_len:]
                values = fullrow[self.key1_len:self.key1_len+self.values_len]
                actual_crow = self.crows.get(key1, None)
                if actual_crow == None:
                    self.crows[key1] = {key2: [values, set((ver,))]}
                else:
                    actual_sub_crow = actual_crow.get(key2, None)
                    if actual_sub_crow == None:
                        self.crows[key1][key2] = [values, set((ver,))]
                    else:
                        self.crows[key1][key2][0] = values
                        self.crows[key1][key2][1].add(ver)

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
                        sql_insert_value.append(str(ver))
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
        c = db.cursor(db)
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

