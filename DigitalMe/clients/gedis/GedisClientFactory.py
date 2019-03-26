from Jumpscale import j

from .GedisClient import GedisClient

JSConfigBase = j.application.JSBaseConfigsClass


class GedisClientCmds:

    def __init__(self, client):
        self._client = client
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


class GedisClientFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.clients.gedis"
    _CHILDCLASS = GedisClient

    # def _init(self):
    #     self._template_engine = None
    #     self._template_code_client = None
    #     self._code_model_template = None

    # def configure(self, namespace="default", host="localhost", port=5000, secret="", ssl=False, ssl_cert_file=""):
    #     data = {
    #         "host": host,
    #         "port": port,
    #         "namespace": namespace,
    #         "adminsecret_": secret,
    #         "ssl": ssl,
    #         'sslkey': ssl_cert_file,
    #     }
    #     return j.application.JSBaseConfigsClass.get(self,name=name, **data).cmds
    #
    #     return self.get(namespace=namespace, host=host, port=port, secret=secret,ssl=ssl, ssl_cert_file=ssl_cert_file)
    #
    # def get(self, name):
