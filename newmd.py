import os
import tempfile
import requests
import shutil
import store


class HTTPPool(store.Pool):
    def __init__(self, url, spec):
        super(HTTPPool, self).__init__(url, spec)
        self._tmpdir = tempfile.mkdtemp()

    def _gen_path(self, hsh):
        url = super(HTTPPool, self)._gen_path(hsh)
        dest = self._tmpdir + '/' + os.path.basename(url)
        res = requests.get(url, stream=True)
        if res.status_code != 200:
            return dest
        with open(dest, 'wb') as f:
            if url.endswith('.gz'):
                while True:
                    chunk = res.raw.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
            else:
                f.write(res.content)
        return dest

    def load_refs(self):
        res = requests.get(self._refpath)
        for line in res.text.split('\n')[:-1]:
            v, k = line.split()
            self.refs[k] = v

    def load(self, hsh):
        o = super(HTTPPool, self).load(hsh)
        if o is not None:
            print('Receive object: %s' % hsh)
        return o

    def clean(self):
        shutil.rmtree(self._tmpdir)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.clean()
