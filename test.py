#!/usr/bin/python3
import sys
from rpmmd import RpmmdPool, Repomd, Primary
from store import Pool

head = sys.argv[1]
url = sys.argv[2]

master = RpmmdPool(url)
slave = Pool({0: Repomd, 1: Primary})

o = master.get(head)
slave.put(o)
o = slave.get(head)

while True:
    missing = o.walk()
    if not missing:
        break
    for h in missing:
        o = master.get(h)
        slave.put(o)

master.clean()
