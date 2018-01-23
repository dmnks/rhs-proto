# rhs-proto
Recursive hash store

## Example

### Compatibility mode

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

### Native metadata format

On server:

```
$ ./rhs convert /repos/fedora27 /repos/fedora27rhs
$ tree /repos/fedora27
/repos/fedora27/
└── repodata
    ├── 48986ce4583cd09825c6d437150314446f0f49fa1a1bd62dcfa1085295030fe9-primary.xml.gz
    ├── bf1798cb9f7e364c68f7ae143f9d715c81576eb6e2ba0007c6247baa0c0a0aaa-filelists.xml.gz
    ├── db434ff174a0a9afa983f7721dda9caaa1d9b6e35517e504e002f824faa87002-comps-Everything.x86_64.xml.gz
    └── repomd.xml

1 directory, 4 files
$ tree /repos/fedora27rhs
/repos/fedora27rhs/
├── objects
│   ├── 2c
│   │   └── df6927097c6a406afd36a0a1f00603f0cd40fa85d7ba2fbe662dc41df9d806
│   └── 48
│       └── 986ce4583cd09825c6d437150314446f0f49fa1a1bd62dcfa1085295030fe9
└── refs

3 directories, 3 files
$ cat /repos/fedora27rhs/refs
2cdf6927097c6a406afd36a0a1f00603f0cd40fa85d7ba2fbe662dc41df9d806 fedora27
```

On client:

```
$ ./rhs fetch http://my.server/repos/fedora27rhs/
$ ./rhs checkout fedora27
$ tree /tmp/rhs
/tmp/rhs/
├── checkout
│   └── fedora27
│       ├── primary.xml.gz
│       └── repomd.xml
├── objects
│   ├── 2c
│   │   └── df6927097c6a406afd36a0a1f00603f0cd40fa85d7ba2fbe662dc41df9d806
│   └── 48
│       └── 986ce4583cd09825c6d437150314446f0f49fa1a1bd62dcfa1085295030fe9
└── refs

5 directories, 5 files
