# DESIGN : Documentation of internal data structure and flow

We have few tasks to do, depending on the program which call lkddb library:

- `lkddb.TASK_BUILD`: generate data of one tree (one version of one project)
- `lkddb.TASK_TABLE`: read the data
- `lkddb.TASK_CONSOLIDATE`: merge multiple data (versions, trees)

The idea of data flow:

'[storage ->] tree -> browser -> scanner [-> subscanner] -> table'

'storage': It aggregate data of multiple trees: different projects and different
    versions

'tree': This is the main entity.  One tree for one project (e.g. Linux kernel) and
    for one version.

'browser': selects the different file types, handling them differently
	thus we open a file only once.
	E.g. we have one for C files (`*.c` and `*.h`), one for building files
	(`Makefile` and `Kbuild`), and one for configuration files (`Kconfig`)
	.
	Because of this, we do parsing in two stages: one reading the files
	and the second stage we do the rest of the job (but this time we could
	use info from other files (e.g. *.h)

'scanner': this is the main part: it find the tables on a specific part of
	code.
	Note: one table could have different scanners (e.g. if usage in the
	source if different), or a scanner could have different tables
	Note: instead of table the output could go to subscanner.
	[which are similar to scanner, but using as input only a part of a file]

'table': the container of data
	rows: a list of: a "line" of raw data as dictionary
	fullrows: a list of: a "line" of formatted (string) data as list
		(it is composed of key1, key2 and values elements)
	crows: a dictionary (key1) of dictionary (key2), of (values, all_versions)


#################

- 'kernel' tree: linux kernel tree (from 2.6.0: new build system)
-- 'kver' browser: main Makefile
----- 'kver' table:
-- 'makefiles' browser: all other Makefiles
----- 'firmware' table:
-- 'kconfigs' browser: KConfig (and similar) files
----- 'kconfig' table
----- 'module' table
-- 'sources' browser: *.c and *.h files
--- 'parent_scanner' scanner: scan the devicetables
---- 'pci' subscanner: pci
---- (usb, ieee1394, hid, ccw, ap, acpi, pnp, pnp_card, serio, of, ....)
---- 'i2c_snd'
---- 'platform'
---- 'fs'


================
kind:

("linux-kernel", "device"):
- specific fields
- ...
- deps (kernel CONFIG_ variable)
- filename (relative to kernel root)
- version (only released)

("linux-kernel", "special"):
- specific table


=============
index:
>0 : key1 (in numering order)
0: values (in definition order)
-10<x<0 : key2 (in absolute order)
-77 : ignore
-99 : version (ignore)

kernel:
-1: deps/config  (put in secondary index, first item)
-2: filename (put in secondary index, second item)
-99: version (not indexed)

