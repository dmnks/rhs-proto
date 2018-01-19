#!/usr/bin/python3
import sys
from rpmmd import RpmmdPool, Repomd, Primary
from store import Store, Pool

url = sys.argv[1]

master = RpmmdPool(url)
slave = Pool({0: Repomd, 1: Primary})
store = Store(slave)
store.fetch(master)
master.clean()
