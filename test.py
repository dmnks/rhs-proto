import sys
from rpmmd import RpmmdPool, Repomd, Primary
from store import Pool

url = sys.argv[1]
hsh = 'd8eb50173e29c8a5c81b2883f89bc29cbb97f6b9e3d7a59f19e8e0b896556f2d'

master = RpmmdPool(url)
slave = Pool({0: Repomd, 1: Primary})

repomd = master.get(hsh)
print(repomd.index)

master.clean()
