from Jumpscale import j

from .GedisClient import GedisClient

JSConfigBase = j.application.JSFactoryBaseClass


class GedisClientCmds:

    def __init__(self, client):
        self._client = client
        self.models = client.models
        self.__dict__.update(client.cmds.__dict__)

    def __str__(self):
        output = "Gedis Client: (instance=%s) (address=%s:%-4s)" % (
            self._client.name,
            self._client.host,
            self._client.port
        )
        if self._client.data.ssl:
            # FIXME: we should probably NOT print the key. this is VERY private information
            output += "\n(ssl=True, certificate:%s)" % self._client.sslkey
        return output

    __repr__ = __str__


class GedisClientFactory(JSConfigBase):
    __jslocation__ = "j.clients.gedis"
    _CHILDCLASS = GedisClient

    def _init(self):
        self._template_engine = None
        self._template_code_client = None
        self._code_model_template = None

    def get(self, name='main', configureonly=False, **kwargs):
        client = JSConfigBase.get(self, name=name, **kwargs)
        if configureonly:
            return

        if client._connected:
            return GedisClientCmds(client)

    def configure(self, name="main", host="localhost", port=5000, secret="", namespace="default",
                  ssl=False, ssl_cert_file="", reset=False,):
        data = {
            "host": host,
            "port": str(port),
            "namespace": namespace,
            "adminsecret_": secret,
            "ssl": ssl,
            'sslkey': ssl_cert_file,
        }
        return self.get(name=name, **data)
