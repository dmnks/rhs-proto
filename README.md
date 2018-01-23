# rhs-proto
Recursive hash store

## Example
```
$ ./rhs fetch --compat http://download.fedoraproject.org/pub/fedora/linux/releases/26/Server/x86_64/os/
$ ./rhs fetch --compat http://download.fedoraproject.org/pub/fedora/linux/releases/27/Server/x86_64/os/
$ ./rhs checkout fedora26
$ ./rhs checkout fedora27
$ tree /tmp/rhs
/tmp/rhs/
├── checkout
│   ├── fedora26
│   │   ├── primary.xml.gz
│   │   └── repomd.xml
│   └── fedora27
│       ├── primary.xml.gz
│       └── repomd.xml
├── objects
│   ├── 09
│   │   └── e30a2ae2f355b1b3414154208d6f6a7b386854e5186708f638f93ff552df8d
│   ├── 62
│   │   └── 8384d8bc78e281d398bb645832966813572319e09bc34a188973fee943dfba
│   ├── 8b
│   │   └── 82e9335da484a1d943162029626fb356e9403f030d95463a398da4430a3cfa
│   └── d0
│       └── e359dd7a814ffcf47395b6cbf800c28d3aff631b8fb3ca6ee1a0976da23614
└── refs

8 directories, 9 files
$ cat /tmp/rhs/refs
628384d8bc78e281d398bb645832966813572319e09bc34a188973fee943dfba fedora26
d0e359dd7a814ffcf47395b6cbf800c28d3aff631b8fb3ca6ee1a0976da23614 fedora27
```
