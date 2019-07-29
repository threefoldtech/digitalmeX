from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass
from .ThreebotServer import ThreeBotServer


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


