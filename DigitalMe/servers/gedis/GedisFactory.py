import os

from Jumpscale import j

from .GedisServer import GedisServer
from .GedisCmds import GedisCmds
from .GedisChatBot import GedisChatBotFactory

JSConfigFactory = j.application.JSBaseConfigsClass


class GedisFactory(JSConfigFactory):
    __jslocation__ = "j.servers.gedis"
    _CHILDCLASS = GedisServer

    def geventserver_get(self, instance=""):
        """
        return gedis_server

        j.servers.gedis.geventserver_get("test")


        """
        server = self.get(instance=instance)
        return server.gedis_server

    def configure(self, name="test", port=8889, host="127.0.0.1", ssl=False, password="", configureclient=False):

        data = {"port": port, "host": host, "password_": password, "ssl": ssl, "name": name}

        server = self.get(**data)
        if configureclient:
            server.client_configure()  # configures the client
        return server

    def _cmds_get(self, key, data):
        """
        Used in client only, starts from data (python client)
        """
        namespace, name = key.split("__")
        return GedisCmds(namespace=namespace, name=name, data=data)

    def test(self, name="basic"):
        """
        it's run all tests
        kosmos 'j.servers.gedis.test()'

        """
        self._test_run(name=name)
