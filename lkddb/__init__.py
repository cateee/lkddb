#!/usr/bin/python
#: lkddb/__init__.py : generic definitions (and classes) for lkddb
#
#  Copyright (c) 2000,2001,2007-2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import pickle
import sqlite3
import logging

import lkddb.log

logger = logging.getLogger(__name__)

# tasks
TASK_BUILD = 1       # scan and build lkddb
TASK_TABLE = 2       # read (and ev. format) tables
TASK_CONSOLIDATE = 3 # consolidate trees (with versions)

PICKLE_PROTOCOL = 4


def init(options):
    lkddb.log.init(options)


class Error(Exception):
    pass


class ParserError(Error):
    def __init__(self, message):
        self.message = message


class DataError(Error):
    def __init__(self, message):
        self.message = message


class InternalError(Error):
    def __init__(self, message):
        self.message = message


#
# Generic classes for device_class and source_trees
#


class Storage:
    """Container of trees, as data file

    The data contains:
        - _trees: list of 'tree' objects
        - _versions: a set of tree versions
        - _tables: list of 'table' names
        - _consolided: 'True'.  Trees are always consolidated
    """

    def __init__(self, trees):
        self.available_trees = {}   # tree_name -> tree
        self.available_tables = {}  # table_name -> (tree_name, table)
        self.loaded_trees = {}	    # tree_name -> tree
        for tree in trees:
            self.available_trees[tree.name] = tree
            for tab_name, tab in tree.tables.items():
                self.available_tables[tab_name] = (tree.name, tab)

    def read_data(self, filename):
        logger.info("=== Reading data-file to consolidate: %s" % filename)
        try:
            with open(filename, 'rb') as f:
                data = pickle.load(f)
        except (EnvironmentError, pickle.PickleError) as e:
            raise DataError("Error reading file '%s': %s" % (filename, e))
        try:
            trees = data['_trees']
        except KeyError:
            raise DataError("Invalid data in file '%s', possibly it is a non aggregated lkddb.data file" % filename)
        consolidated = data.get('_consolidated', False)
        for tree_name in trees:
            logger.info("== Consolidating tree '%s'" % tree_name)
            try:
                tree = self.available_trees[tree_name]
            except KeyError:
                logger.error("Found an unknown tree '%s' in data '%s'" % (tree_name, filename))
                continue
            tree.read_consolidate(consolidated, data)
            self.loaded_trees[tree_name] = tree

    def write_data(self, filename):
        logger.info("=== Writing data '%s'" % filename)
        data = {}
        trees = []
        tables = []
        versions = set(())
        trees_keys = sorted(self.loaded_trees.keys())
        for tree_key in trees_keys:
            tree = self.loaded_trees[tree_key]
            new_data = tree.write_consolidate()
            new_tables = new_data['_tables']
            trees.append(tree.name)
            tables.extend(new_tables)
            versions.update(new_data['_versions'])
            for t in new_tables:
                if t in data:
                    raise DataError("two different trees share the table name '%s'" % t)
                data[t] = new_data[t]
        data['_trees'] = trees
        data['_tables'] = tables
        data['_versions'] = versions
        data['_consolidated'] = True
        with open(filename, 'wb') as f:
            pickle.dump(data, f, protocol=PICKLE_PROTOCOL)


class Tree:
    """defines sources of a project with task, a base path, a version and some related browsers"""
    # e.g. kernel sources

    def __init__(self, name):
        self.name = name

        self.browsers = []
        self.scanners = []
        self.tables = {}
        self.views = []
        self.version = None
        self.version_dict = {}
        self.consolidated_versions = set(())

    def get_strversion(self):
        if self.version is None:
            self.retrieve_version()
        return self.version[2]

    def retrieve_version(self):
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
    
    #
    # persistent data:
    #   - data:  in python pickle format  [rows (raw)]
    #   - lines: in text (line based) format [fullrows (sort+uniq)]
    #   - sql:   in SQL database
    #   - consolidate: in python pickle format [crows (with all versions)]
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
        lkddb.log.phase("Writing 'data'")
        persistent_data = {}
        persistent_data['_version'] = self.version
        persistent_data['_tables'] = tuple(sorted(self.tables.keys()))
        persistent_data['_trees'] = [self.name]
        for t in self.tables.values():
            persistent_data[t.name] = t.rows
        with open(filename, 'wb') as f:
            pickle.dump(persistent_data, f, protocol=PICKLE_PROTOCOL)

    def read_data(self, filename):
        lkddb.log.phase("Reading data-file: '%s'" % filename)
        try:
            with open(filename, 'rb') as f:
                persistent_data = pickle.load(f)
        except (EnvironmentError, pickle.PickleError) as e:
            raise DataError("Error reading file '%s': %s" % (filename, e))
        try:
            tables = persistent_data['_tables']
            trees = persistent_data['_trees']
            self.version = persistent_data['_version']
        except KeyError:
            raise DataError("Invalid data in file '%s'" % filename)
        if self.name not in trees:
            raise DataError("File '%s' is not a valid data file for tree %s" % (filename, self.name))
        for t in self.tables.values():
            if t.name not in tables:
                logger.info("Table '%s' not found in '%s'" % (t.name, filename))
                continue
            logger.info("Reading table '%s'" % t.name)
            rows = persistent_data.get(t.name, None)
            if rows is not None:
                t.rows = rows
                t.restore()

    def read_consolidate(self, consolidated, persistent_data):
        if not consolidated:
            ver = persistent_data['_version']
            self.consolidated_versions.add(ver)
        else:
            ver = None
            self.consolidated_versions.update(persistent_data['_versions'])
        for t in self.tables.values():
            logger.info("Reading table '%s'" % t.name)
            rows = persistent_data.get(t.name, None)
            if rows is not None:
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
                logger.info("Table '%s' is empty" % t.name)
                if not hasattr(self, 'crows'):
                    self.crows = {}

    def write_consolidate(self):
        persistent_data = {}
        persistent_data['_tables'] = tuple(sorted(self.tables.keys()))
        persistent_data['_versions'] = self.consolidated_versions
        for t in self.tables.values():
            persistent_data[t.name] = t.crows
        return persistent_data

    def write_list(self, filename):
        lkddb.log.phase("Writing 'list'")
        lines = []
        tables_keys = sorted(self.tables.keys())
        for tk in tables_keys:
            new = self.tables[tk].get_lines()
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
        lkddb.log.phase("Writing 'sql'")
        ver = self.version
        db = sqlite3.connect(filename)
        c = db.cursor()
        #lfddb = lkddb.create_generic_tables(c)
        for t in self.tables.values():
            t.prepare_sql(ver)
            t.create_sql(c)
        db.commit()
        c.close()
        for t in self.tables.values():
            t.to_sql(db)
        db.commit()
        db.close()


class Browser():
    """scan a tree. In two phases: 'scan' read the tree; 'finalize' do the rest"""
    # two phases: only after reading all sources, we can do cross-references

    def __init__(self, name):
        self.name = name

    def scan(self):
        logger.info("=== Browse and scan sourced for %s" % self.name)

    def finalize(self):
        logger.info("=== Finalizing scan for %s" % self.name)


class Scanner:

    def __init__(self, name):
        self.name = name


class Table:
    """The real container of data"""

    def __init__(self, name):
        self.name = name
        self.rows = []
        self.fullrows = []
        self.consolidate = {}
        self.cols = None
        self.line_fmt = None
        self.line_len = None
        self.col_len = None
        self.key1_len = None
        self.key2_len = None
        self.values_len = None
        self.indices = None
        self.indices_inv = None
        self.line_templ = None

    def init_cols(self):
        line_fmt = []
        line_indices = []
        for col_index, col_name, col_line_fmt, col_sql in self.cols:
            if col_line_fmt:
                line_indices.append(col_index)
                line_fmt.append(col_line_fmt)
        self.line_fmt = tuple(line_fmt)
        self.line_len = len(line_fmt)
        self.col_len = len(self.cols)
        self.key1_len = len([v for v in line_indices if v > 0])
        self.key2_len = len([v for v in line_indices if -10 < v < 0])
        self.values_len = len([v for v in line_indices if v == 0])
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
                raise InternalError("unknown code of index")
        self.indices = tuple(indices)
        self.indices_inv = tuple(indices_inv)
        if line_fmt:
            self.line_templ = self.name + (" %s" * self.key1_len + " %s" * self.values_len +
                                           " : %s" * self.key2_len + '\n')

    def add_fullrow(self, row):
        # format data
        r = []
        try:
            for f, v in zip(self.line_fmt, self.pre_row_fmt(row)):
                r.append(f(v))
        except AssertionError:
            logger.exception("Assertion in table %s in row %s" % (self.name, row))
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
        lkddb.log.phase("Formatting " + self.name)
        for row in self.rows:
            self.add_fullrow(row)

    def get_lines(self):
        # TODO: change to an iterator ########################
        lkddb.log.phase("Printing lines in " + self.name)
        lines = []
        fullrow = None
        try:
            for fullrow in self.fullrows:
                lines.append(self.line_templ % fullrow)
        except TypeError:
            logger.exception("Exception in %s, templ: '%s', row: %s" % (self.name, self.line_templ[:-1], fullrow))
        return lines

    def consolidate_table(self, consolidated, ver):
        lkddb.log.phase("Consolidating lines in " + self.name)
        if not hasattr(self, 'crows'):
            self.crows = {}

        # consolidating
        if consolidated:
            for key1, values1 in self.crows_tmp.items():
                for key2, values2 in values1.items():
                    values, all_versions = values2
                    actual_crow = self.crows.get(key1, None)
                    if actual_crow is None:
                        self.crows[key1] = {key2: [values, all_versions]}
                    else:
                        actual_sub_crow = actual_crow.get(key2, None)
                        if actual_sub_crow is None:
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
                if actual_crow is None:
                    self.crows[key1] = {key2: [values, {ver}]}
                else:
                    actual_sub_crow = actual_crow.get(key2, None)
                    if actual_sub_crow is None:
                        self.crows[key1][key2] = [values, {ver}]
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
            self.sql_create = ("CREATE TABLE IF NOT EXISTS " + self.name + " (" +
                " id INTEGER PRIMARY KEY,\n" +
                ",\n ".join(sql_create_col) + " );" )
            self.sql_insert = ("INSERT OR UPDATE INTO " + self.name + " (" +
                ", ".join(sql_cols) + ") VALUES ("+
                ", ".join(("?",)*len(sql_cols)) + ");")

    def create_sql(self, cursor):
        cursor.execute(self.sql_create)
        sql = "INSERT OR IGNORE INTO `tables` (name) VALUES (" + self.name +");"
        cursor.execute(sql)

#    def to_sql(self, db):
#        c = db.cursor(db)
#        for row in self.rows:
#            c.execute(self.sql_insert, row + self.extra_data)
#        db.commit()
#        c.close()

#
#def create_generic_tables(c):
#    sql = "CREATE TABLE IF NOT EXISTS `tables` (id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
#    c.execute(sql)
#    sql = "CREATE TABLE IF NOT EXISTS `filename` (id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
#    c.execute(sql)
#    sql = "CREATE TABLE IF NOT EXISTS `config` (id INTEGER PRIMARY KEY, name TEXT UNIQUE);"
#    c.execute(sql)
#    sql = """CREATE TABLE IF NOT EXISTS `deps` (
# `config_id` INTEGER REFERENCE `config`,
# `item_id` INTEGER,
# `table_id` INTEGER REFERENCE `tables`
#);"""
#
