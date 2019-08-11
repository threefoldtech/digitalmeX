from Jumpscale import j
import os
import gevent
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass


class ThreeBotServer(j.application.JSBaseConfigClass):
    """
    Open Publish factory
    """

    _SCHEMATEXT = """
        @url = jumpscale.open_publish.1
        name* = "main" (S)
        executor = tmux,corex (E)
        adminsecret_ = "123456"  (S)      
        """

    def _init(self, **kwargs):
        self.content = ""
        self._rack = None
        self._gedis_server = None
        self._startup_cmd = None

    @property
    def rack(self):
        if not self._rack:
            self._rack = j.servers.rack.get()
        return self._rack

    @property
    def gedis_server(self):
        if not self._gedis_server:
            self._gedis_server = j.servers.gedis.get("main", port=8900)
        return self._gedis_server

    def start(self, background=False):
        """

        kosmos 'j.servers.threebot.default.start()'

        :param background:
        :return:
        """

        if not background:
            zdb = j.servers.zdb.new("threebot", adminsecret_=self.adminsecret_, executor=self.executor)
            zdb.start()

            openresty = j.servers.openresty.get("threebot", executor=self.executor)
            # j.servers.openresty.build() # build from threebot builder or server from a seperate call
            # wikis_load_cmd = """
            # from Jumpscale import j
            # j.tools.markdowndocs.load_wikis()
            # """
            # wikis_loader = j.servers.startupcmd.get(
            #     "wikis_loader", cmd_start=wikis_load_cmd, timeout=60 * 60, executor=self.executor, interpreter="python"
            # )
            # if not wikis_loader.is_running():
            #     wikis_loader.start()

            openresty.install()
            openresty.start()

            j.servers.sonic.default.start()

            # add system actors
            self.gedis_server.actors_add("%s/base_actors" % self._dirpath)
            self.gedis_server.chatbot.chatflows_load("%s/base_chatflows" % self._dirpath)

            app = j.servers.gedis_websocket.default.app
            self.rack.websocket_server_add("websocket", 4444, app)

            dns = j.servers.dns.get_gevent_server("main", port=5354)  # for now high port
            self.rack.add("dns", dns)

            self.rack.add("gedis", self.gedis_server.gevent_server)
            self.rack.bottle_server_add()

            # add user added packages
            for package in j.tools.threebotpackage.find():
                package.prepare(gedis_server=self.gedis_server, package_root=package.path)
                package.start()

            self.rack.start()

        else:
            # the MONKEY PATCH STATEMENT IS NOT THE BEST, but prob required for now
            if self.startup_cmd.is_running():
                self.startup_cmd.stop()
            self.startup_cmd.start()

    def stop(self):
        """
        :return:
        """
        self.startup_cmd.stop(waitstop=False, force=True)

    @property
    def startup_cmd(self):
        if not self._startup_cmd:
            cmd_start = """
            from gevent import monkey
            monkey.patch_all(subprocess=False)
            from Jumpscale import j
            server = j.servers.threebot.get("{name}", executor='{executor}')
            server.start(background=False)
            """.format(
                name=self.name, executor=self.executor
            )
            cmd_start = j.core.tools.text_strip(cmd_start)
            startup = j.servers.startupcmd.get(name="threebot_{}".format(self.name), cmd_start=cmd_start)
            startup.executor = self.executor
            startup.interpreter = "python"
            startup.timeout = 60
            startup.ports = [8900, 4444, 8090]
            self._startup_cmd = startup
        return self._startup_cmd

    # def auto_update(self):
    #     while True:
    #         self._log_info("Reload for docsites done")
    #         gevent.sleep(300)
