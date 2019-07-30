from .ThreebotServer import ThreeBotServer
from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass


class ThreeBotServersFactory(j.application.JSBaseConfigsClass):
    """
    Factory for 3bots
    """

    __jslocation__ = "j.servers.threebot"
    _CHILDCLASS = ThreeBotServer

    def _init(self):
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.get("default")
        return self._default

    def install(self):
        j.builders.web.openresty.install()
        j.builders.runtimes.lua.install()
        j.builders.db.zdb.install()
        j.builders.apps.sonic.install()

    def bcdb_get(self, name, secret="", use_zdb=False):
        return self.default.bcdb_get(name, secret, use_zdb)

    def test(self):
        """

        kosmos 'j.servers.threebot.test()'

        :return:
        """

        s = self.default
        s.start()

        j.shell()
