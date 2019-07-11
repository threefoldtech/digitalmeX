from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass


class ThreeBotServer(j.application.JSBaseConfigClass):
    """
    Open Publish factory
    """

    _SCHEMATEXT = """
        @url = jumpscale.open_publish.1
        name* = "main" (S)
        executor = "corex"
        adminsecret_ = "123456"
        """

    def start(self):

        # j.clients.git.getContentPathFromURLorPath(OPEN_PUBLISH_REPO, pull=False)
        url = "https://github.com/threefoldtech/jumpscale_weblibs"
        weblibs_path = j.clients.git.getContentPathFromURLorPath(url, pull=True)
        j.sal.fs.symlink(
            "{}/static".format(weblibs_path), "{}/static/weblibs".format(self.open_publish_path), overwriteTarget=False
        )

        # # Start Lapis Server
        # self._log_info("Starting Lapis Server")
        # cmd = "moonc . && lapis server".format(self.open_publish_path)
        # lapis = j.servers.startupcmd.get(name="Lapis", cmd=cmd, path=self.open_publish_path)
        # if lapis.running:
        #     self.reload_server()
        # else:
        #     lapis.start()

        j.servers.zdb.configure(adminsecret=self.adminsecret, executor=self.executor)
        j.servers.zdb.start()

        # Start bcdb server and create corresponding dns namespace
        bcdb = self.bcdb_get(name="dns", use_zdb=True)
        # Start DNS Server
        self.dns_server = j.servers.dns.get(bcdb=bcdb)
        gevent.spawn(self.dns_server.serve_forever)

        # Start Sonic Server
        sonic_server = j.servers.sonic.default
        sonic_server.start()
        j.tools.markdowndocs.sonic_client_set(sonic_server.default_client)

        # Start Gedis Server
        self._log_info("Starting Gedis Server")
        self.gedis_server = j.servers.gedis.configure(
            name=self.gedis.name,
            port=self.gedis.port,
            host=self.gedis.host,
            ssl=self.gedis.ssl,
            password=self.gedis.password_,
        )
        actors_path = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "base_actors")
        self.gedis_server.actors_add(actors_path)
        chatflows_path = j.sal.fs.joinPaths(j.sal.fs.getDirName(os.path.abspath(__file__)), "base_chatflows")
        self.gedis_server.chatbot.chatflows_load(chatflows_path)
        self.gedis_server.start()

    def bcdb_get(self, name, secret="", use_zdb=False):
        return self.default.bcdb_get(name, secret, use_zdb)

    def start(self, background=True):
        """
        kosmos 'j.tools.open_publish.start()'
        """
        if background:
            cmd = "kosmos 'j.tools.open_publish.start(background=False)'"
            j.tools.tmux.execute(cmd, window="Open Publish", pane="main", reset=False)
            self._log_info("waiting for gedis to start on port {}".format(self.default.gedis.port))
            res = j.sal.nettools.waitConnectionTest("localhost", self.default.gedis.port, timeoutTotal=120)
            if not res:
                raise RuntimeError("Failed to start Open Publish")
            self._log_info("Open Publish framework started")
        else:
            self.default.servers_start()
