#!/usr/bin/python
#:  utils.py : utilities and data exchange infrastructure for lkddb
#
#  Copyright (c) 2000,2001,2007,2008  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 for details

import sys, os, time, sqlite3, traceback

#
# globals variables
#

# starting cwd
program_cwd    = None
# kernel directory and their lenght
kerneldir      = None
# actual kernel version in form of: 0x020627 or -1 for HEAD
version_number = None
version_string = None
# connector of sqlite database
conn	       = None
# options
options        = None
# actual file parsed (for debug message)
filename       = None


start_time = None

def init(options_, logfile_, kerneldir_):
    global start_time, options, kerneldir
    options       = options_
    kerneldir     = kerneldir_

    start_time = time.time()

    log_init(options.verbose, logfile_)
    db_init(options.dbfile)
    devices_init()

#
# logs
#

_logfile = sys.stdout
_verbose = 0

def log_init(verbose=1, logfile=sys.stdout):
    global _verbose, _logfile
    _verbose = verbose
    _logfile = logfile

def log(message):
    if _verbose:
        _logfile.write("%3.1f: " % (time.time()-start_time) + message + "\n")

def log_extra(message):
    if _verbose > 1:
        _logfile.write(message + "\n")

def die(errcode, message):
    sys.stderr.write(message + "\n")
    sys.exit(errcode)

#
# Temporary database: 'devices' and 'db'
#

devices = []  # []-> scanner[class instance], data[scanner dependent], dep[set], filename[string]
db = []       # []-> line[string]

def devices_init():
    global devices, db
    devices = []
    db = []

def devices_add(scanner, data, dep, filename):
    "add raw device data"
    devices.append((scanner, data, dep, filename))


def lkddb_build():
    "convert the raw data into db data"
    global filename, c
    lines = []
    for scanner, res, dep, filename in devices:
	depstr = list(dep)
	depstr.sort()
	depstr = " ".join(depstr)
	dep = map(get_config_id, dep)
	filename_id = get_filename_id(filename)
	dep_id = get_dep_id(dep)
	try:
	    line = scanner.formatter(res)
	except:
	    print "-" * 50
	    print "EXCEPTION: utils.py/lkddb_build ", filename, scanner.name, res
	    traceback.print_exc(file=sys.stdout)
	    print "-" * 50
	    continue
	if not line:
	    continue
        line_txt = "lkddb\t" + scanner.name + "\t" + scanner.format % line  + (
            "\t:: %s\t:: %s\n" % (depstr, filename) )
 	set_line(scanner, line, dep_id, filename_id, line_txt)
	lines.append(line_txt)
    lines.sort()
    lines2 = []
    old = ""
    for line in lines:
        if line == old:
            continue
        old = line
        lines2.append(line)
    if options.lkddb_list:
        f = open(os.path.join(program_cwd, options.lkddb_list), "w")
        f.writelines(lines2)
        f.close()

#
# lkddb sqlite support
#

def get_config_id(config):
    row = configs.get(config, None)
    if row:
	min_ver, max_ver = row[1], row[2]
        changed = 0
        if version_number > 0  and  max_ver < version_number:
            max_ver = version_number
            changed = 2
	if min_ver == -1  and  version_number > 0:
	    min_ver = version_number
	    changed = 1
        elif min_ver > version_number  and  version_number > 0:
            min_ver = version_number
            changed = 1
        if changed:
	    c = conn.cursor()
	    c.execute("INSERT OR REPLACE INTO configs (config_id, config, min_ver, max_ver) VALUES (?,?,?,?);",
		(row[0], config, min_ver, max_ver))
	    conn.commit()
        return row[0]
    c = conn.cursor()
    c.execute("INSERT INTO configs (config, min_ver, max_ver) VALUES (?,?,?);",
                (config, version_number, version_number))
    row = (c.execute("SELECT config_id FROM configs WHERE config=?;",
		(config,)).fetchone()[0] , version_number, version_number)
    conn.commit()
    configs[config] = row
    return row[0]

def get_filename_id(filename):
    ret = filenames.get(filename, None)
    if ret:
        return ret
    c = conn.cursor()
    c.execute("INSERT INTO filenames (filename) VALUES (?);", (filename,))
    ret = c.execute("SELECT filename_id FROM filenames WHERE filename=?;",
                (filename,)).fetchone()[0]
    conn.commit()
    filenames[filename] = ret
    return ret


dependencies = {}
rdependencies = {}
max_dep = -1
def get_dep_id(deps):
    global max_dep
    c = conn.cursor()
    if not dependencies:
	for dep_id, config_id in c.execute(
		"SELECT dep_id, config_id FROM deps;"):
	    old = dependencies.setdefault(dep_id, [])
	    old.append(config_id)
	    dependencies[dep_id] = old
	    if dep_id > max_dep:
		max_dep = dep_id
	for dep_id, dep_list in dependencies.iteritems():
	    dep_list.sort()
	    rdependencies.setdefault(tuple(dep_list), dep_id)
    deps.sort()
    deps = tuple(deps)
    ret = rdependencies.get(deps)
    if ret:
	return ret
    max_dep += 1
    for d in deps:
	c.execute("INSERT INTO deps (dep_id, config_id) VALUES (?,?)", (max_dep, d))
    rdependencies[deps] = max_dep
    return max_dep


def set_line(scanner, line, dep_id, filename_id, line_txt):
    c = conn.cursor()

    row = c.execute(scanner.select_id, line).fetchone()
    if row:
	id = row[0]
	row = c.execute(
"SELECT line_id, dep_id, min_ver, max_ver FROM lines " +
"WHERE scanner_id=? AND id=? AND filename_id=?;",
		(scanner.scanner_id, id, filename_id)).fetchone()
	if row:
	    line_id, dep_id2, min_ver, max_ver = row
	    changed = 0
            if version_number > 0  and  max_ver < version_number:
                max_ver = version_number
                changed = 2
            if min_ver == -1  and  version_number > 0:
                min_ver = version_number
                changed = 1
            elif min_ver > version_number  and  version_number > 0:
                min_ver = version_number
                changed = 1
	    if dep_id2 != dep_id:
		if changed == 2  or  version_number < 0:
		    # update dependencies only on newer kernels
		    dep_id2 = dep_id
		    changed = 3
	    if changed:
		c.execute(
'INSERT OR REPLACE INTO lines (line_id, scanner_id, id, dep_id, filename_id, min_ver, max_ver, line) VALUES (?,?,?,?,?,?,?,?)',
		    (line_id, scanner.scanner_id, id, dep_id2, filename_id, min_ver, max_ver, line_txt))
		conn.commit()
	    return
    else:
        c.execute(scanner.insert_id, line)
        id = c.execute(scanner.select_id, line).fetchone()[0]
    c.execute("INSERT INTO lines (scanner_id, id, dep_id, filename_id, min_ver, max_ver, line) "+
	"VALUES (?,?,?,?,?,?,?);",
	(scanner.scanner_id, id, dep_id, filename_id, version_number, version_number, line_txt))
    conn.commit()


def new_scanner_table(name, format, db_attrs):
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS " + name + "s (" +
        name + "_id  INTEGER PRIMARY KEY, " +
            " TEXT, ".join(db_attrs) + " TEXT);")

    c.execute("INSERT OR IGNORE INTO scanners (name, db_attrs, format) VALUES (?,?,?);",
		(name, ",".join(db_attrs), format))
    ret = c.execute("SELECT scanner_id FROM scanners WHERE name=?;",
                    (name,)).fetchone()[0]
    conn.commit()
    return ret


def db_init(dbfile):
    global conn, configs, filenames
    conn = sqlite3.connect(dbfile)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS version (" +
	"type       INTEGER UNIQUE, " +  # 0 : lkddb, 1 : kernel
	"min_ver    INTEGER DEFAULT 16777215, " +
    	"max_ver    INTEGER DEFAULT 0, " +
    	"head_tag   TEXT DEFAULT '(none)' ); ")

    c.execute("CREATE TABLE IF NOT EXISTS scanners (" +
	"scanner_id INTEGER PRIMARY KEY, " +
	"name	    TEXT UNIQUE, " +
	"db_attrs   TEXT, " +
	"format     TEXT); ")

    c.execute("CREATE TABLE IF NOT EXISTS filenames (" +
	"filename_id INTEGER PRIMARY KEY, " +
	"filename    TEXT UNIQUE );")
    c.execute("CREATE TABLE IF NOT EXISTS configs (" +
        "config_id  INTEGER PRIMARY KEY, " +
	"config	    TEXT UNIQUE, " +
        "min_ver    INTEGER DEFAULT 16777215, " +
        "max_ver    INTEGER DEFAULT 0 ); ")
    c.execute("CREATE TABLE IF NOT EXISTS lines (" +
	"line_id     INTEGER PRIMARY KEY, " +
        "scanner_id  INTEGER, " +
	"id          INTEGER, " +
        "dep_id      INTEGER, " +
        "filename_id INTEGER, " +
        "min_ver     INTEGER DEFAULT 16777215, " +
        "max_ver     INTEGER DEFAULT 0, " +
	"line	     TXT, " +
        "UNIQUE(scanner_id, id, filename_id) );")

    c.execute("CREATE TABLE IF NOT EXISTS deps (" +
        "dep_id     INTEGER, " +
        "config_id  INTEGER ); ")

    c.execute("CREATE TABLE IF NOT EXISTS kkeys (" +
        "kkey_id   INTEGER PRIMARY KEY, " +
        "key       TEXT, " +
        "UNIQUE(key) );")
    c.execute("CREATE TABLE IF NOT EXISTS kitems (" +
	"kitem_id   INTEGER PRIMARY KEY, " +
        "config_id  INTEGER, " +
	"filename_id INTEGER, " +
	"kkey_type  INTEGER, " +
	"descr      TEXT, " +
	"depends    TEXT, " +
	"help	    TEXT, " +
	"UNIQUE(config_id, filename_id, kkey_type, descr) );")

    conn.commit()

    configs = {}
    for config_id, config, min_ver, max_ver in  c.execute(
            "SELECT config_id, config, min_ver, max_ver FROM configs;"):
        configs[config] = (config_id, min_ver, max_ver)
    filenames = {}
    for filename_id, filename in c.execute(
            "SELECT filename_id, filename FROM filenames;"):
        filenames[filename] = filename_id

