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
        os.link(self.path, repodata + '/repomd.xml')
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
    pass


class RpmmdPool(object):
    def __init__(self, url):
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

        k2o = {'repomd': Repomd, 'primary': Primary}
        self._table = {}
        for key, cls in k2o.items():
            item = data[key]
            path = item['location_href']
            path = os.path.join(self._destdir, path)
            obj = cls(path, magic=False)
            self._table[obj.hash] = obj

    def clean(self):
        shutil.rmtree(self._destdir)

    def get(self, hsh):
        return self._table[hsh]