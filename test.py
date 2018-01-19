#!/usr/bin/python3
import sys
import store
import rpmmd

url = sys.argv[1]

master = rpmmd.Pool(url)
slave = store.Pool(rpmmd.spec)
st = store.Store(slave)
st.fetch(master)
master.clean()
