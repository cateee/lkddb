#!/usr/bin/python
#: test_log.py : unit test for lkddb.log
#
#  Copyright (c) 2017  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details


import unittest

import lkddb.log

versioned_cases = (
    ("logfile", "logfile"),
    ("", ""),
    ("%.log", "1.2.3.log"),
    ("%%.log", "%.log"),
    ("%", "1.2.3"),
    ("%%", "%"),
    ("lkddb-%.log", "lkddb-1.2.3.log"),
    ("lkddb-%%.log", "lkddb-%.log"),
    ("lkddb-%.%.log", "lkddb-1.2.3.1.2.3.log"),
    ("lkddb%%-%.log", "lkddb%-1.2.3.log"),
    ("lkddb-%.%%log", "lkddb-1.2.3.%log")
)


class TestVersionedNameForLog(unittest.TestCase):

    def test_get_versioned_name(self):
        v = "1.2.3"
        for input, output in versioned_cases:
            self.assertEqual(lkddb.log._get_versioned_name(input, v), output)


if __name__ == '__main__':
        unittest.main()
