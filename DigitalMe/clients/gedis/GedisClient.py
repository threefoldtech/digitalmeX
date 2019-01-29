import imp
import os

from Jumpscale import j
from redis.connection import ConnectionError

JSConfigBase = j.application.JSBaseConfigClass


class Models():
    def __init__(self):
        pass


class CmdsBase():
    def __init__(self):
        pass


class GedisClient(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.gedis.client
    name* = "main"
    host = "127.0.0.1" (S)
    port = 9900 (ipport)
    namespace = "default" (S)
    password_ = "" (S)
    ssl = False (B)
    sslkey = "" (S)
    configureonly=False (B)
    """

    def _init(self):
        j.clients.gedis.latest = self
        self.namespace = self.data.namespace

        self.code_generated_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "gedis", self.name, "client")
        j.sal.fs.createDir(self.code_generated_dir)
        j.sal.fs.touch(j.sal.fs.joinPaths(self.code_generated_dir, '__init__.py'))

        if self.data.configureonly:
            return

        self._redis = None  # connection to server
        self._models = None
        self._cmds = None
        self.cmds_meta = {}

        self._connect()
        self.ping()
        self._connected = True

        self.redis.execute_command("select", self.namespace)

        # download remote actors commands to generate client code
        cmds_meta = self.redis.execute_command("api_meta", self.namespace)
        cmds_meta = j.data.serializers.msgpack.loads(cmds_meta)
        for key, capnpbin in cmds_meta["cmds"].items():
            if "__model_" not in key:
                self.cmds_meta[key] = j.servers.gedis._cmds_get(key, capnpbin).cmds

    def ping(self):
        test = self.redis.execute_command("ping")
        if test != b'PONG':
            raise RuntimeError('Can not ping server')
        return True

    @property
    def cmds(self):
        if self._cmds is None:
            self._cmds = CmdsBase()
            for nsfull, cmds_ in self.cmds_meta.items():
                cmds = CmdsBase()
                cmds.cmds = cmds_
                cmds.name = nsfull.replace(".", "_")
                location = nsfull.replace(".", "_")
                cmds_name_lower = nsfull.split(".")[-1].strip().lower()
                cmds.cmds_name_lower = cmds_name_lower

                name = "gedisclient_cmds_%s" % (cmds_name_lower)

                tpath = "%s/templates/template.py.jinja" % (j.clients.gedis._dirpath)
                cl = j.tools.jinja2.code_python_render(obj_key="CMDS", path=tpath,
                                                       overwrite=True, name=name,
                                                       objForHash=None, obj=cmds)

                if "__" in cmds_name_lower:
                    cmds_name_lower = cmds_name_lower.split("__", 1)[1]

                setattr(self.cmds, cmds_name_lower, cl(client=self, cmds=cmds.cmds))
                self._logger.debug("cmds:%s" % name)
        return self._cmds

    def _connect(self):
        """
        this gets you a redis instance, when executing commands you have to send the name of the function without
        the postfix _cmd as is, do not capitalize it
        if it is testtest_cmd, then you should call it by testtest

        :return: redis instance
        """
        if self._redis is None:
            addr = self.data.host
            port = self.data.port
            secret = self.data.password_
            ssl_certfile = self.data.sslkey

            if self.data.ssl:
                if not self.data.sslkey:
                    ssl_certfile = j.sal.fs.joinPaths(os.path.dirname(self.code_generated_dir), 'ca.crt')
                self._logger.info("redisclient: %s:%s (ssl:True  cert:%s)" % (addr, port, ssl_certfile))
            else:
                self._logger.info("redisclient: %s:%s " % (addr, port))

            self.redis = j.clients.redis.get(
                ipaddr=addr,
                port=port,
                password=secret,
                ssl=self.data.ssl,
                ssl_ca_certs=ssl_certfile,
                ping=False
            )
        return self._redis
