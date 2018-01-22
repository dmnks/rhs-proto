#!/usr/bin/python3
import sys
import store
import rpmmd

url = sys.argv[1]

master = rpmmd.MasterPool(url)
slave = rpmmd.SlavePool('/tmp/rhs', rpmmd.spec)
st = store.Store(slave)
st.fetch(master)
st.checkout('fedora27')
master.clean()
