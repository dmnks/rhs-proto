#!/usr/bin/python3
import sys
from rpmmd import RpmmdPool, Repomd, Primary
from store import Pool

hroot = sys.argv[1]
url = sys.argv[2]

master = RpmmdPool(url)
slave = Pool({0: Repomd, 1: Primary})

o = master.get(hroot)
slave.put(o)
o = slave.get(hroot)

hmissing = o.walk()
for h in hmissing:
    o = master.get(h)
    slave.put(o)

master.clean()
