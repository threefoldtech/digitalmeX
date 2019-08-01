import imp
import os
import nacl

from Jumpscale import j
from redis.connection import ConnectionError

JSConfigBase = j.application.JSBaseConfigClass


class WGServer(j.application.JSBaseConfigClass):
    _SCHEMATEXT = """
    @url = jumpscale.wireguard.server.1
    name* = "main"
    sshclient_name = "" (S)    
    """

    def _init(self, **kwargs):
        self._ssh = None

    @property
    def ssh(self):
        if not self._ssh:
            self._ssh = j.clients.ssh.get(name=self.sshclient_name, die=True)
        return self._ssh

    @property
    def executor(self):
        self.ssh.executor


class WGServers(j.application.JSBaseConfigsClass):
    _CHILDCLASS = WGServer
    _name = "servers"
