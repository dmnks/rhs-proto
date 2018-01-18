import hashlib
import os


# Abstract class
class Object(object):
    def __init__(self, path, magic=True):
        with open(path, 'rb') as f:
            if magic:
                # Skip the magic byte
                f.read(1)
            data = f.read()

        self.path = path
        self.data = data
        self.index = self.parse(data)

        m = hashlib.new('sha256')
        m.update(data)
        self.hash = m.hexdigest()

    def parse(self, data):
        return []


class Pool(object):
    def __init__(self, magic, base='/tmp/rhs/objects', width=2, depth=2):
        self._table = {}
        self.magic = magic
        self.base = base
        self.width = width
        self.depth = depth

    def _gen_path(self, hsh):
        w = self.width
        d = self.depth
        cmps = [hsh[i:i+w] for i in range(0, w*d, w)]
        cmps[-1] += hsh[w*d:]
        return os.path.join(self.base, *cmps)

    def _read_type(self, path):
        with open(path, 'rb') as f:
            m = int.from_bytes(f.read(1), byteorder='big')
            return self.magic[m]

    def get(self, hsh):
        try:
            return self._table[hsh]
        except KeyError:
            # Load from file (if any)
            path = self._gen_path(hsh)
            if not os.path.exists(path):
                return None
            cls = self._read_type(path)
            obj = cls(path)
            self._table[hsh] = obj
            return obj

    def put(self, obj):
        if self.get(obj.hash) is not None:
            return obj.hash

        for m, cls in self.magic.items():
            if cls == obj.__class__:
                break
        else:
            raise Exception()  # FIXME
        path = self._gen_path(obj.hash)
        prefix = os.path.split(path)[0]
        if not os.path.exists(prefix):
            os.makedirs(prefix)
        with open(path, 'wb') as f:
            f.write(bytes([m]))
            f.write(obj.data)

        return obj.hash

    def save(self):
        pass
