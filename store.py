import hashlib
import os
import gzip
import binascii


def gen_hash(data):
    m = hashlib.new('sha256')
    m.update(data)
    return m.hexdigest()


# Abstract class
class Object(object):
    def __init__(self, path, pool=None):
        data = self.read(path)
        self._pool = pool
        self._data = data
        self.index = self.parse(data)
        self.hash = gen_hash(data)

    def read(self, path):
        with open(path, 'rb') as f:
            return f.read()

    def write(self, path):
        with open(path, 'wb') as f:
            f.write(self._data)

    def parse(self, data):
        raise NotImplementedError()

    def walk(self):
        total = []
        for hsh in self.index:
            obj = self._pool.get(hsh)
            if obj is None:
                total.append(hsh)
                continue
            hashes = obj.walk()
            total.extend(hashes)
        return total


class Pool(object):
    def __init__(self, spec, base='/tmp/rhs/objects', width=2, depth=2):
        self._table = {}
        self._spec = spec

        self.base = base
        self.width = width
        self.depth = depth
        self.refs = []
        self.head = None

    def _gen_path(self, hsh):
        w = self.width
        d = self.depth
        cmps = [hsh[i:i+w] for i in range(0, w*d, w)]
        cmps[-1] += hsh[w*d:]
        return os.path.join(self.base, *cmps)

    def detect(self, path):
        with open(path, 'rb') as f:
            gz = binascii.hexlify(f.read(2)) == b'1f8b'
        if gz:
            f = gzip.open(path, 'rt')
        else:
            f = open(path, 'r')
        f.seek(self._spec['offset'])
        header = f.read(self._spec['headerlen'])
        f.close()
        return self._spec['headers'][header]

    def get(self, hsh):
        try:
            return self._table[hsh]
        except KeyError:
            # Load from file (if any)
            path = self._gen_path(hsh)
            if not os.path.exists(path):
                return None
            cls = self.detect(path)
            obj = cls(path, pool=self)
            self._table[hsh] = obj
            return obj

    def put(self, obj):
        if self.get(obj.hash) is not None:
            return obj.hash
        path = self._gen_path(obj.hash)
        prefix = os.path.split(path)[0]
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        obj.write(path)
        return obj.hash


class Store(object):
    def __init__(self, slave):
        self.slave = slave

    def _fetch_refs(self, master):
        self.slave.refs = master.refs
        self.slave.head = master.head

    def _fetch_objs(self, master, ref):
        h = self.slave.refs[ref]
        o = self.slave.get(h)
        if not o:
            o = master.get(h)
            self.slave.put(o)
            o = self.slave.get(h)

        while True:
            missing = o.walk()
            if not missing:
                break
            for h in missing:
                o = master.get(h)
                self.slave.put(o)

    def fetch(self, master):
        self._fetch_refs(master)
        self._fetch_objs(master, self.slave.head)
