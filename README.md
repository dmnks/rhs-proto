# rhs-proto
Recursive hash store

## Example
```
$ ./rhs fetch http://download.fedoraproject.org/pub/fedora/linux/releases/26/Server/x86_64/os/
$ ./rhs checkout fedora26
$ ./rhs fetch http://download.fedoraproject.org/pub/fedora/linux/releases/27/Server/x86_64/os/
$ ./rhs checkout fedora27
$ tree /tmp/rhs
```
