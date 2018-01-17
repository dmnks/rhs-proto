import librepo
import store


class Repomd(store.Object):
    def parse(self, data):
        h = librepo.Handle()
        r = librepo.Result()
        h.setopt(librepo.LRO_REPOTYPE, librepo.LR_YUMREPO)
        h.setopt(librepo.LRO_URLS, ['/tmp/myrepo'])
        h.setopt(librepo.LRO_LOCAL, True)
        try:
            h.perform(r)
        except librepo.LibrepoException as e:
            pass
        m = r.getinfo(librepo.LRR_YUM_REPOMD)
        return [m[t]['checksum'] for t in ['primary']]


class Primary(store.Object):
    pass
