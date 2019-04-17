#!/usr/bin/python

import fnmatch
import os
import os.path
import re
import sys

datadir = os.environ.get('DATA', 'data')

count_files = []  # [((x, y, z, ...), 'x.y.z', path), ...] for kernel x.y.z


def numeric_version_from(point):
    if point.isdigit():
        return int(point)
    if point.startswith('rc'):
        return -0x200 + int(point[2:])
    if point.startswith('pre'):
        return -0x300 + int(point[3:])
    if point.startswith('g'):
        return 0
    assert False, 'invalid subversion "{}"'.format(point)


for fn in fnmatch.filter(os.listdir(datadir), 'lkddb-*.list.counts'):
    ver_str =  fn[6:-12]
    ver = [numeric_version_from(v) for v in re.split('[-.]', ver_str)]
    count_files.append((ver, ver_str, fn))
count_files.sort()

base_line = [0] * len(count_files)

res = {}

for i, (ver, ver_str, fn) in enumerate(count_files):
    with open(os.path.join(datadir, fn)) as f:
        for line in f:
            count, typ = line.strip().split()
            if typ not in res:
                res[typ] = base_line.copy()
            try:
                val = int(count)
            except ValueError:
                val = count
            res[typ][i] = val

del res['kver']

print('_VER,' + ','.join(ver_str for ver, ver_str, fn in count_files))
for typ in sorted(res.keys()):
    print(typ + ',' + ','.join(str(c) for c in res[typ]))
