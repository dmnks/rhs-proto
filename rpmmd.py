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


def parse_url_repo(url):
    comps = url.split('/')
    distro = comps[4]
    release = comps[7]
    return distro + release


def parse_local_repo(path):
    if path[-1] == '/':
        path = path[:-1]
    return os.path.basename(path)


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


class Pool(store.Pool):
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


class LibrepoPool(store.Pool):
    def __init__(self, url, base, width=2, depth=2):
        if base is None:
            base = '/dev/null'
            save = False
        else:
            save = True
        super(LibrepoPool, self).__init__(base, spec, width, depth)

        # Fetch metadata
        h = librepo.Handle()
        r = librepo.Result()
        h.repotype = librepo.LR_YUMREPO
        h.urls = [url]
        h.local = not url.startswith('http')
        self._repodir = h.destdir = tempfile.mkdtemp()
        try:
            h.perform(r)
        except librepo.LibrepoException as e:
            pass
        basic = r.getinfo(librepo.LRR_RPMMD_REPO)
        full = r.getinfo(librepo.LRR_YUM_REPOMD)

        # Add repomd to the result
        path = basic['repomd']
        with open(path, 'r') as f:
            csum = gen_hash(f.read())
        basic['paths']['repomd'] = path
        full['repomd'] = {'checksum': csum, 'location_href': path}

        # Generate objects
        for key in ['repomd', 'primary']:
            path = basic['paths'][key]
            csum = full[key]['checksum']
            data = self._read(path)
            cls = self.detect(data)
            obj = cls(csum, data, path, self)
            if save:
                self.save(obj)
            else:
                self._table[csum] = obj

        # Generate refs
        if h.local:
            repo = parse_local_repo(url)
        else:
            repo = parse_url_repo(url)
        self.refs = {repo: full['repomd']['checksum']}
        if save:
            self.save_refs()

        # Clean up
        if save:
            # We already saved our objects into this pool so no need to keep
            # the original download around
            self.clean()

    def clean(self):
        shutil.rmtree(self._repodir)

    def load(self, hsh):
        o = super(LibrepoPool, self).load(hsh)
        if o is not None:
            print('Receive object: %s' % hsh)
        return o

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.clean()
