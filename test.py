#!/usr/bin/python3
import sys
from rpmmd import RpmmdPool, RpmmdSpec
from store import Store, Pool

url = sys.argv[1]

master = RpmmdPool(url)
slave = Pool(RpmmdSpec)
store = Store(slave)
store.fetch(master)
master.clean()
