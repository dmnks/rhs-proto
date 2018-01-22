import os
import shutil
import tempfile
import hashlib
import librepo
import store


def gen_hash(data):
    m = hashlib.new('sha256')
    m.update(data.encode('utf-8'))
    return m.hexdigest()


class Repomd(store.Object):
    def _createrepo(self):
        d = tempfile.mkdtemp()
        repodata = d + '/repodata'
        os.mkdir(repodata)
        self.checkout(repodata + '/repomd.xml')
        return d

    def parse(self, data):
        h = librepo.Handle()
        r = librepo.Result()
        h.repotype = librepo.LR_YUMREPO
        d = self._createrepo()
        h.urls = [d]
        h.local = True
        try:
            h.perform(r)
        except librepo.LibrepoException as e:
            pass
        result = r.getinfo(librepo.LRR_YUM_REPOMD)
        shutil.rmtree(d)
        return [result[t]['checksum'] for t in ['primary']]


class Primary(store.Object):
    def parse(self, data):
        return []


spec = {
    'headers': {'<r': Repomd, '<m': Primary},
    'offset': len('<?xml version="1.0" encoding="UTF-8"?>') + 1,
}


class SlavePool(store.Pool):
    def checkout(self, obj, name):
        path = self._chkpath + '/' + name
        if os.path.exists(path):
            shutil.rmtree(path)
        os.makedirs(path)
        repomd = obj
        repomd.checkout(path + '/repomd.xml')
        phash = repomd.index[0]
        primary = self.load(phash)
        primary.checkout(path + '/primary.xml.gz')


class MasterPool(store.Pool):
    def __init__(self, url):
        # Fetch metadata
        h = librepo.Handle()
        r = librepo.Result()
        h.repotype = librepo.LR_YUMREPO
        h.urls = [url]
        self._destdir = h.destdir = tempfile.mkdtemp()
        try:
            h.perform(r)
        except librepo.LibrepoException as e:
            pass
        result = r.getinfo(librepo.LRR_YUM_REPOMD)

        # Add repomd to data
        path = self._destdir + '/repodata/repomd.xml'
        with open(path, 'r') as f:
            repomd_hash = gen_hash(f.read())
        result['repomd'] = {'checksum': repomd_hash, 'location_href': path}

        # Generate objects
        k2o = {'repomd': Repomd, 'primary': Primary}
        self._table = {}
        for key, cls in k2o.items():
            item = result[key]
            csum = item['checksum']
            path = item['location_href']
            path = os.path.join(self._destdir, path)
            data = self._read(path)
            obj = cls(csum, data, path, self)
            self._table[csum] = obj

        # Generate refs
        repo = self._parse_name(url)
        self._refs = {repo: repomd_hash}

    def _parse_name(self, url):
        comps = url.split('/')
        distro = comps[4]
        release = comps[7]
        return distro + release

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        shutil.rmtree(self._destdir)

    def load(self, hsh):
        print('Receive object: %s' % hsh)
        return self._table[hsh]

    def save(self, hsh):
        raise NotImplementedError()
