#!/usr/bin/python
#: utils/check-kernel-version.py : update kernel and data
#
#  Copyright (c) 2011  Giacomo A. Catenazzi <cate@cateee.net>
#  This is free software, see GNU General Public License v2 (or later) for details

import sys
import os
import os.path
import subprocess
import optparse
import fnmatch
import glob



def make(options, kerneldir, datadir):
    ver = getversion(kerneldir)
    filename = "lkddb-" + ver + ".data"
    if os.path.exists(os.path.join(datadir, filename)):
        sys.stdout.write('\n')
        sys.stdout.flush()
        sys.exit(1)
    sys.stdout.write(filename + '\n')
    sys.stdout.flush()
    sys.exit(0)
    

def getversion(kerneldir):
    version_dict = {}
    f = open(os.path.join(self.kerneldir, "Makefile"))
    for i in range(10):
        line = f.readline().strip()
        if not line or line[0] == '#':
                continue
            try:
                label, value = line.split('=', 1)
            except ValueError:
                continue
            version_dict[label.strip()] = value.strip()
        f.close()
        assert(version_dict.has_key("VERSION"))
        assert(version_dict.has_key("PATCHLEVEL"))
        assert(version_dict.has_key("SUBLEVEL"))
        assert(version_dict.has_key("EXTRAVERSION"))
        version_dict['local_ver'] = subprocess.Popen("/bin/sh scripts/setlocalversion",
                shell=True, cwd=self.kerneldir,
                stdout=subprocess.PIPE).communicate()[0].strip() # .replace("-dirty", "")
        fullversion = ( version_dict["VERSION"] + "." + version_dict["PATCHLEVEL"] + "." +
                        version_dict["SUBLEVEL"] +  version_dict["EXTRAVERSION"] + 
                        version_dict['local_ver'] )
        print "Actual kernel has version %s" % fullversion



if __name__ == "__main__":

    usage = "Usage: %prog [options] kerneldir datadir"
    parser = optparse.OptionParser(usage=usage)
    parser.set_defaults(verbose=1, dbfile="lkddb", sversioned=False)
    parser.add_option("-q", "--quiet",  dest="verbose",
                      action="store_const", const=0,
                      help="inhibit messages")
    parser.add_option("-v", "--verbose", dest="verbose",
                      action="count",
                      help="increments verbosity")
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error("missing mandatory arguments: kernel source directory and lkddb data directory")
    kerneldir = os.path.normpath(args[0])
    if kerneldir[-1] != "/":
        kerneldir += "/"
    datadir = os.path.normpath(args[1])
    if datadir[-1] != "/":
        datadir += "/"

    make(options, kerneldir, datadir)

