from Jumpscale import j

from .WGClient import WGClients
from .WGServer import WGServers


class WGFactory(j.application.JSBaseConfigsFactoryClass):
    """
    wireguard factory

    works over ssh

    """

    __jslocation__ = "j.tools.wireguard"

    _CHILDCLASSES = [WGClients, WGServers]

    def test(self):
        """
        kosmos -p 'j.tools.wireguard.test()"
        :return:
        """
