import imp
import os

from Jumpscale import j
from redis.connection import ConnectionError

JSConfigBase = j.application.JSBaseConfigClass


class GedisClientActors():
    def __init__(self):
        pass


class GedisClient(JSConfigBase):
    _SCHEMATEXT = """
    @url = jumpscale.gedis.client
    name* = "main"
    host = "127.0.0.1" (S)
    port = 8888 (ipport)
    namespace = "default" (S)
    password_ = "" (S)
    ssl = False (B)
    sslkey = "" (S)
    
    """

    def _init(self):
        # j.clients.gedis.latest = self
        self._namespace = self.data.namespace

        self._code_generated_dir = j.sal.fs.joinPaths(j.dirs.VARDIR, "codegen", "gedis", self.name, "client")
        j.sal.fs.createDir(self._code_generated_dir)
        j.sal.fs.touch(j.sal.fs.joinPaths(self._code_generated_dir, '__init__.py'))
        self._reset()

    def _update_trigger(self, key, val):
        self._reset()

    def _reset(self):
        self._redis_ = None  # connection to server
        # self._models = None
        self._actors = None

    def ping(self):
        test = self._redis.execute_command("ping")
        if test != b'PONG':
            return False
        return True

    @property
    def actors(self):

        if self._actors is None:
            assert self.ping()
            self._actorsmeta = {}
            # self._redis.execute_command("select", self.namespace)
            self._client_actors = GedisClientActors()
            cmds_meta = self._redis.execute_command("api_meta_get", self.namespace)
            cmds_meta = j.data.serializers.msgpack.loads(cmds_meta)
            if cmds_meta["cmds"] == {}:
                raise RuntimeError("did not find any actors in namespace:%s" % self.namespace)
            for key, capnpbin in cmds_meta["cmds"].items():
                if "__model_" in key:
                    raise RuntimeError("aa")
                actor_name = key.split("__")[1]
                self._actorsmeta[actor_name] = j.servers.gedis._cmds_get(key, capnpbin)

            # at this point the schema's are loaded only for the namespace identified (is all part of metadata)
            for actorname, actormeta in self._actorsmeta.items():
                tpath = "%s/templates/GedisClientGenerated.py" % (j.clients.gedis._dirpath)

                cl = j.tools.jinja2.code_python_render(obj_key="GedisClientGenerated", path=tpath,
                                                       overwrite=True, name=actorname,
                                                       objForHash=None, obj=actormeta)

                o = cl(client=self)
                setattr(self._client_actors, actorname, o)
                self._log_debug("cmds:%s" % name)
            j.shell()

        self._actors = self._client_actors
        return self._actors

    @property
    def _redis(self):
        """
        this gets you a redis instance, when executing commands you have to send the name of the function without
        the postfix _cmd as is, do not capitalize it
        if it is testtest_cmd, then you should call it by testtest

        :return: redis instance
        """
        if self._redis_ is None:
            addr = self.data.host
            port = self.data.port
            secret = self.data.password_
            ssl_certfile = self.data.sslkey

            if self.data.ssl:
                if not self.data.sslkey:
                    ssl_certfile = j.sal.fs.joinPaths(os.path.dirname(self._code_generated_dir), 'ca.crt')
                self._log_info("redisclient: %s:%s (ssl:True  cert:%s)" % (addr, port, ssl_certfile))
            else:
                self._log_info("redisclient: %s:%s " % (addr, port))

            self._redis_ = j.clients.redis.get(
                ipaddr=addr,
                port=port,
                password=secret,
                ssl=self.data.ssl,
                ssl_ca_certs=ssl_certfile,
                ping=False,
                fromcache=False
            )
        return self._redis_

    # def __getattr__(self, name):
    #     if name.startswith("_") or name in self._methods() or name in self._properties():
    #         return self.__getattribute__(name)
    #     return self.cmds.__getattribute__(name)



    def _methods(self,prefix=""):
        if prefix.startswith("_"):
            return JSConfigBase._methods(self,prefix=prefix)

        res = self._cmds._methods

        for i in ["ping"]:
            if i not in res:
                res.append(i)

        return res

