#!/usr/bin/python
#: utils/view.py : view contents of lkddb data files
#
#  Copyright (c) 2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import sys
import os.path
import optparse
import shelve

LIMIT=10

def main_view(options, args):
    filename = args[0]
    assert os.path.isfile(filename), "Could not find data file %s" % filename
    data = shelve.open(filename)
    if data.has_key('_consolidated'):
        print("data file '%s' is consolidated" % filename)
    else:
        print("data file '%s' is not consolidated" % filename)
    recursive_view(options, data, args[1:], "data")


def recursive_view(options, data, args, name):
    if not args:
        final_view(options, data, name)
    now = args[0]
    if now == "/keys/":
        final_view(options, data.keys(), name+".keys()")
    elif now[0] == "[" and now[-1] == "]":
        ### handle slices
        v1 = int(now[1:-1])
        final_view(options, data[v1], name+now)
    else:
        final_view(options, data[now], name+"['"+now+"']")
        

def final_view(options, data, name):
    if type(data) == type({}):
        print("dictionary %s has length %s" % (name, len(data)))
        count = 0
        for key, value in data.iteritems():
            count += 1
            if count > options.limit:
                print("...")
                break
            else:
                print("%s   <=   %s" % (key, value))
    elif type(data) == type([]) or type(data) == type(()):
        print("list %s has length %s" % (name, len(data)))
        count = 0
        for value in data:
            count += 1
            if count > options.limit:
                print("...")
                break
            else:
                print(value)
    else:
        print("data %s has type %s" % (name, type(data)))
        print(data)



#
# main
#

if __name__ == "__main__":

    usage = "Usage: %prog [options] file.data [key... [filter]]"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, limit=10)
    parser.add_option("-q", "--quiet",  dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    parser.add_option("-l", "--limit", dest="limit",
                      action="store",
                      help="number of item to display")
    (options, args) = parser.parse_args()

    options.limit = int(options.limit)
    main_view(options, args)


