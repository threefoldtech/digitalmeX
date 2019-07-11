from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass
from .ThreebotServer import ThreeBotServer


class ThreeBotServers(j.application.JSBaseConfigsFactoryClass):
    """
    Factory for 3bots
    """

    __jslocation__ = "j.servers.threebot"
    _CHILDCLASSES = [ThreeBotServer]

    def test(self):
        j.shell()
