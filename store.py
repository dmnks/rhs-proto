import os
import gzip
import binascii


# Abstract class
class Object(object):
    def __init__(self, hsh, data, path, pool):
        self._data = data
        self._path = path
        self._pool = pool
        self.hash = hsh
        self.index = self.parse(data)

    def parse(self, data):
        raise NotImplementedError()

    def walk(self):
        total = []
        for hsh in self.index:
            obj = self._pool.load(hsh)
            if obj is None:
                total.append(hsh)
                continue
            hashes = obj.walk()
            total.extend(hashes)
        return total

    def checkout(self, path):
        self._pool._write(self, path)


class Pool(object):
    def __init__(self, base, spec, width=2, depth=2):
        self._table = {}
        self._spec = spec
        self._refs = {}
        self._refpath = base + '/refs'
        self._objpath = base + '/objects'
        self._chkpath = base + '/checkout'

        self.base = base
        self.width = width
        self.depth = depth

    @property
    def refs(self):
        if not self._refs:
            for f in os.listdir(self._refpath):
                with open(self._refpath + '/' + f) as f:
                    k = os.path.basename(f.name)
                    self._refs[k] = f.read()[:-1]
        return self._refs

    @refs.setter
    def refs(self, value):
        path = self._refpath
        if not os.path.exists(path):
            os.makedirs(path)
        for k, v in value.items():
            with open(path + '/' + k, 'w') as f:
                f.write(v + '\n')
        self._refs = value

    def _gen_path(self, hsh):
        w = self.width
        d = self.depth
        cmps = [hsh[i:i+w] for i in range(0, w*d, w)]
        cmps[-1] += hsh[w*d:]
        return os.path.join(self._objpath, *cmps)

    def _read(self, path):
        with open(path, 'rb') as f:
            gz = binascii.hexlify(f.read(2)) == b'1f8b'
        if gz:
            f = gzip.open(path, 'rt')
        else:
            f = open(path, 'r')
        data = f.read()
        f.close()
        return data

    def _write(self, obj, path):
        os.link(obj._path, path)

    def detect(self, data):
        headers = self._spec['headers']
        start = self._spec['offset']
        end = start + len(list(headers.keys())[0])
        return headers[data[start:end]]

    def load(self, hsh):
        try:
            return self._table[hsh]
        except KeyError:
            # Load from file (if any)
            path = self._gen_path(hsh)
            if not os.path.exists(path):
                return None
            data = self._read(path)
            cls = self.detect(data)
            obj = cls(hsh, data, path, self)
            self._table[hsh] = obj
            return obj

    def save(self, obj):
        if self.load(obj.hash) is not None:
            return obj.hash
        path = self._gen_path(obj.hash)
        prefix = os.path.split(path)[0]
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        self._write(obj, path)
        obj._path = path
        obj._pool = self
        self._table[obj.hash] = obj
        return obj.hash

    def checkout(self, obj, path):
        raise NotImplementedError()


class Store(object):
    def __init__(self, slave):
        self.slave = slave

    def _fetch_refs(self, master):
        self.slave.refs = master.refs

    def _fetch_objs(self, master, ref):
        h = self.slave.refs[ref]
        root = self.slave.load(h)
        if root is None:
            root = master.load(h)
            if root is None:
                return
            self.slave.save(root)

        missing = set()
        while True:
            wanted = set(root.walk())
            wanted -= missing
            if not wanted:
                break
            for h in wanted:
                o = master.load(h)
                if o is None:
                    missing.add(h)
                else:
                    self.slave.save(o)

    def fetch(self, master):
        self._fetch_refs(master)
        for ref in self.slave.refs:
            self._fetch_objs(master, ref)

    def checkout(self, ref):
        h = self.slave.refs[ref]
        o = self.slave.load(h)
        name = ref
        self.slave.checkout(o, name)
