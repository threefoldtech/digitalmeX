import imp
import os
import nacl

from Jumpscale import j
from redis.connection import ConnectionError

JSConfigBase = j.application.JSBaseConfigClass


class GedisClientActors(j.application.JSBaseClass):
    pass


class GedisClientSchemas(j.application.JSBaseClass):
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
        j.sal.fs.touch(j.sal.fs.joinPaths(self._code_generated_dir, "__init__.py"))
        self._redis_ = None
        self._reset()

    def _update_trigger(self, key, val):
        self._reset()

    def _reset(self):
        self._redis_ = None  # connection to server
        # self._models = None
        self._actors = None

    def ping(self):
        test = self._redis.execute_command("ping")
        if test != b"PONG":
            return False
        return True

    def auth(self, bot_id):
        nacl_cl = j.data.nacl.get()
        nacl_cl._load_privatekey()
        signing_key = nacl.signing.SigningKey(nacl_cl.privkey.encode())
        epoch = str(j.data.time.epoch)
        signed_message = signing_key.sign(epoch.encode())
        cmd = "auth {} {} {}".format(bot_id, epoch, signed_message)
        res = self._redis.execute_command(cmd)
        return res

    @property
    def actors(self):

        if self._actors is None:
            assert self.ping()
            self._actorsmeta = {}
            # self._redis.execute_command("select", self.namespace)
            self._actors = GedisClientActors()
            self.schemas = GedisClientSchemas()

            cmds_meta = self._redis.execute_command("api_meta_get", self.namespace)
            cmds_meta = j.data.serializers.msgpack.loads(cmds_meta)
            if cmds_meta["cmds"] == {}:
                raise RuntimeError("did not find any actors in namespace:%s" % self.namespace)
            for key, data in cmds_meta["cmds"].items():
                if "__model_" in key:
                    raise RuntimeError("aa")
                actor_name = key.split("__")[1]
                self._actorsmeta[actor_name] = j.servers.gedis._cmds_get(key, data)
                # a = self._actorsmeta[actor_name]

            # at this point the schema's are loaded only for the namespace identified (is all part of metadata)
            for actorname, actormeta in self._actorsmeta.items():
                tpath = "%s/templates/GedisClientGenerated.py" % (j.clients.gedis._dirpath)

                cl = j.tools.jinja2.code_python_render(
                    obj_key="GedisClientGenerated",
                    path=tpath,
                    overwrite=True,
                    name=actorname,
                    objForHash=None,
                    obj=actormeta,
                )

                o = cl(client=self)
                setattr(self._actors, actorname, o)
                self._log_info("cmds for actor:%s" % actorname)

                def process_url(url):
                    url = url.replace(".", "_")
                    if url.startswith("actors_"):
                        url = "_".join(url.split("_")[2:])
                    return url

                for name, cmd in actormeta.cmds.items():
                    if cmd.schema_in and not cmd.schema_in.url.startswith("actors."):
                        setattr(self.schemas, process_url(cmd.schema_in.url), cmd.schema_in)
                    if cmd.schema_out and not cmd.schema_out.url.startswith("actors."):
                        setattr(self.schemas, process_url(cmd.schema_out.url), cmd.schema_out)

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
                    ssl_certfile = j.sal.fs.joinPaths(os.path.dirname(self._code_generated_dir), "ca.crt")
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
                fromcache=False,
            )
        return self._redis_

    # def __getattr__(self, name):
    #     if name.startswith("_") or name in self._methods() or name in self._properties():
    #         return self.__getattribute__(name)
    #     return self.cmds.__getattribute__(name)

    def _methods(self, prefix=""):
        if prefix.startswith("_"):
            return JSConfigBase._methods(self, prefix=prefix)
        res = self.actors._methods()
        for i in ["ping"]:
            if i not in res:
                res.append(i)

        return res
