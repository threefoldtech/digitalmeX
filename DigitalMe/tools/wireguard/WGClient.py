import imp
import os
import nacl

from Jumpscale import j
from redis.connection import ConnectionError

JSConfigBase = j.application.JSBaseConfigClass


class WGClient(JSConfigBase):
    _SCHEMATEXT = """
        @url = jumpscale.wireguard.client.1
        name* = "main"
        servername = "" (S)    
        """
    _name = "servers"

    def _init(self, **kwargs):
        pass


class WGClients(j.application.JSBaseConfigsClass):
    _CHILDCLASS = WGClient
    _name = "clients"
