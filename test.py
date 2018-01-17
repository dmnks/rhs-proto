import sys
from store import Pool
from rpmmd import Repomd, Primary

rpath, ppath = sys.argv[1:3]

pool = Pool({1: Repomd, 2: Primary})
repomd = Repomd(rpath, magic=False)
primary = Primary(ppath, magic=False)
h1 = pool.put(repomd)
h2 = pool.put(primary)

obj1 = pool.get(h1)
obj2 = pool.get(h2)
print(obj1.hash)
print(obj2.hash)
print(obj1.index)
