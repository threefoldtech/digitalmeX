from Jumpscale import j

JSBASE = j.application.JSBaseClass


class system(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)
        self.server = j.servers.gedis.latest

    def ping(self):
        return "PONG"

    def ping_bool(self):
        return True

    # def core_schemas_get(self, namespace):
    #     """
    #     return all core schemas as understood by the server, is as text, can be processed by j.data.schema
    #     """
    #     namespace = namespace.decode()
    #     res = {}
    #     for key, item in j.data.schema.schemas.items():
    #         # TODO: should prob limit to namespace
    #         res[key] = item.text
    #     return j.data.serializers.msgpack.dumps(res)

    def api_meta_get(self, namespace):
        """
        return the api meta information

        """
        namespace = namespace.decode()
        res = {"cmds": {}}
        for key, item in self.server.cmds_meta.items():
            if item.namespace == namespace:
                res["cmds"][key] = item.data._data
        return j.data.serializers.msgpack.dumps(res)

    def filemonitor_paths(self, schema_out):
        """
        return all paths which should be monitored for file changes
        ```out
        paths = (LS)
        ```
        """

        r = schema_out.new()

        # monitor changes for the docsites (markdown)
        for key, item in j.tools.docsites.docsites.items():
            r.paths.append(item.path)

        # monitor change for the webserver  (schema's are in there)
        r.paths.append(j.servers.web.latest.path)

        # changes for the actors
        r.paths.append(j.servers.gedis.latest.code_generated_dir)
        r.paths.append(j.servers.gedis.latest.app_dir + "/actors")
        r.paths.append("%s/systemactors" % j.servers.gedis.path)

        return r

    def filemonitor_event(self, changeobj):
        """
        used by filemonitor daemon to escalate events which happened on filesystem

        ```in
        src_path = (S)
        event_type = (S)
        is_directory = (B)
        ```

        """

        # Check if a blueprint is changed
        # if changeobj.is_directory:
        #     path_parts = changeobj.src_path.split('/')
        #     if path_parts[-2] == 'blueprints':
        #         blueprint_name = "{}_blueprint".format(path_parts[-1])
        #         bp = j.servers.web.latest.app.app.blueprints.get(blueprint_name)
        #         if bp:
        #             self._log_info("reloading blueprint : {}".format(blueprint_name))
        #             del (j.servers.web.latest.app.app.blueprints[blueprint_name])
        #             j.servers.web.latest.app.app.register_blueself._log_info(bp)
        #             return

        # Check if docsite is changed
        if changeobj.is_directory:
            docsites = j.tools.docsites.docsites
            for _, docsite in docsites.items():
                if docsite.path in changeobj.src_path:
                    docsite.load()
                    self._log_info("reloading docsite: {}".format(docsite))
                    return

        # check if path is actor if yes, reload that one
        if not changeobj.is_directory and changeobj.src_path.endswith(".py"):
            paths = list()
            paths.append(j.servers.gedis.latest.code_generated_dir)
            paths.append(j.servers.gedis.latest.app_dir + "/actors")
            paths.append("%s/systemactors" % j.servers.gedis.path)
            # now check if path is in docsites, if yes then reload that docsite only !
            for path in paths:
                if path in changeobj.src_path:
                    actor_name = j.sal.fs.getBaseName(changeobj.src_path)[:-3].lower()
                    namespace = j.servers.gedis.latest.instance + "." + actor_name
                    if namespace in j.servers.gedis.latest.cmds_meta:
                        del j.servers.gedis.latest.cmds_meta[namespace]
                        del j.servers.gedis.latest.actors[namespace]
                        for cmd in list(j.servers.gedis.latest.cmds.keys()):
                            if actor_name in cmd:
                                del j.servers.gedis.latest.cmds[cmd]
                        j.servers.gedis.latest.cmds_add(namespace, path=changeobj.src_path)
                        self._log_info("reloading namespace: {}".format(namespace))
                        return

        return

    def _options(self, args, nr_args=1):
        res = []
        res2 = {}
        key = ""
        nr = 0
        for arg in args:
            nr += 1
            if nr < nr_args + 1:
                val = args[nr - 1].decode()
                res.append(val)
                continue
            else:
                if key == "":
                    key = args[nr - 1].decode()
                    if not j.data.types.string.check(key):
                        raise RuntimeError("%s: key:%s need to be string" % (args, key))
                else:
                    res2[key] = args[nr - 1].decode()
                    key = ""
        return res, res2
