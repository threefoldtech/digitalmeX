from Jumpscale import j

JSConfigBase = j.application.JSFactoryBaseClass
from .GedisClient import GedisClient


class GedisClientCmds():
    def __init__(self):
        pass

    # @property
    # def _config(self):
    #     return self._client.config
    #
    # @property
    # def _config_template(self):
    #     return self._client.config_template

    def __str__(self):
        if self._client.ssl:
            return "Gedis Client: (name=%s) (address=%s:%-4s)\n(ssl=True, certificate:%s)" % (
                self._client.name,
                self._client.host,
                self._client.port,
                self._client.sslkey
            )

        return "Gedis Client: (name=%s) (address=%s:%-4s)" % (
            self._client.name,
            self._client.host,
            self._client.port
        )

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
        # if self.configureonly:
        #     print("CONFIGURE ONLY")
        #     returns

        if client._connected:
            cl = GedisClientCmds()
            cl._client = client
            cl.models = client.models
            cl.__dict__.update(cl._client.cmds.__dict__)
            return cl

    def configure(
        self,
        name="main",
        host="localhost",
        port=5000,
        secret="",
        namespace="default",
        ssl=False,
        ssl_cert_file="",
        reset=False, get=True
    ):

        data = {}

        data["host"] = host
        data["port"] = str(port)
        data["namespace"] = namespace
        data["adminsecret_"] = secret
        data["ssl"] = ssl
        data['sslkey'] = ssl_cert_file

        if get:
            return self.get(instance=instance, data=data, reset=reset)
