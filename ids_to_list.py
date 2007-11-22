#!/usr/bin/python

# convert .ids files into list files

import sys, re

if len(sys.argv) > 1  and  sys.argv[1] != "-":
    infile = open(sys.argv[1])
else:
    infile = sys.stdin

if len(sys.argv) > 2  and  sys.argv[2] != "-":
    outfile = open(sys.argv[2], "w")
else:
    outfile = sys.stdout

if len(sys.argv) > 3:
    prefix = sys.argv[3] + "\t"
else:
    if sys.argv[1].endswith(".ids"):
	prefix = sys.argv[1][:-4] + "\t"
    else:
	prefix = ""

line_re = re.compile(r"^(\t*)(.*?)  (.*)$")

header = True
ids = []

for line in infile:
    if header:
	if line[0] == "#":
	    outfile.write(line)
	else:
	    header = False
	continue
    if line[0] == "#"  or  line.strip() == "":
	continue
    m = line_re.match(line)
    if not m:
	print "ignoring unknow line: ", line,
	continue
    tabs, id, name = m.groups()
    level = len(tabs)
    ids[level:] = [id]
    outfile.write(prefix + " ".join(ids) + "\t" + name + "\n")
    

