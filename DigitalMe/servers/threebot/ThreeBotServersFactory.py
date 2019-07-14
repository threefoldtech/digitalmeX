from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass
from .ThreebotServer import ThreeBotServers


class ThreeBotServersFactory(j.application.JSBaseConfigsFactoryClass):
    """
    Factory for 3bots
    """

    __jslocation__ = "j.servers.threebot"
    _CHILDCLASSES = [ThreeBotServers]

    def _init(self):
        self._default = None

    @property
    def server_default(self):
        if not self._default:
            self._default = self.servers.new(name="default")
        return self._default

    def test(self):
        """

        kosmos 'j.servers.threebot.test()'

        :return:
        """

        s = self.server_default
        s.start()

        j.shell()
