import os
import shutil
import tempfile
import librepo
import store


class Repomd(store.Object):
    def _createrepo(self):
        d = tempfile.mkdtemp()
        repodata = d + '/repodata'
        os.mkdir(repodata)
        self.write(repodata + '/repomd.xml')
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
        data = r.getinfo(librepo.LRR_YUM_REPOMD)
        shutil.rmtree(d)
        return [data[t]['checksum'] for t in ['primary']]


class Primary(store.Object):
    def parse(self, data):
        return []


spec = {
    'headers': {'<r': Repomd, '<m': Primary},
    'headerlen': 2,
    'offset': len('<?xml version="1.0" encoding="UTF-8"?>') + 1,
}


class Pool(object):
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
        data = r.getinfo(librepo.LRR_YUM_REPOMD)
        data['repomd'] = {
            'location_href': self._destdir + '/repodata/repomd.xml',
        }

        # Generate objects
        k2o = {'repomd': Repomd, 'primary': Primary}
        self._table = {}
        for key, cls in k2o.items():
            item = data[key]
            path = item['location_href']
            path = os.path.join(self._destdir, path)
            obj = cls(path)
            self._table[obj.hash] = obj

        # Generate refs
        repo = self._parse_name(url)
        with open(data['repomd']['location_href'], 'rb') as f:
            h = store.gen_hash(f.read())
        self.refs = {repo: h}
        self.head = repo

    def _parse_name(self, url):
        comps = url.split('/')
        distro = comps[4]
        release = comps[7]
        return distro + release

    def clean(self):
        shutil.rmtree(self._destdir)

    def get(self, hsh):
        print('Get master object: %s' % hsh)
        return self._table[hsh]
