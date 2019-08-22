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
        self._openresty_server = None
        j.servers.threebot.current = self

    @property
    def rack(self):
        if not self._rack:
            self._rack = j.servers.rack.get()
        return self._rack

    @property
    def gedis_server(self):
        if not self._gedis_server:
            self._gedis_server = j.servers.gedis.get(f"threebot_{self.name}", port=8901)
        return self._gedis_server

    @property
    def openresty_server(self):
        if not self._openresty_server:
            j.builders.runtimes.lua.install()
            self._openresty_server = j.servers.openresty.get(f"threebot_{self.name}")
            self._openresty_server.install()
        return self._openresty_server

    def _zdb_start(self):
        j.builders.db.zdb.install()
        zdb = j.servers.zdb.new("threebot", adminsecret_=self.adminsecret_, executor=self.executor)
        zdb.start()

    def _sonic_start(self):
        j.servers.sonic.default.start()

    def _load_wikis(self):
        wikis_load_cmd = """
                    from Jumpscale import j
                    j.tools.markdowndocs.load_wikis()
                    """
        wikis_loader = j.servers.startupcmd.get(
            "wikis_loader", cmd_start=wikis_load_cmd, timeout=60 * 60, executor=self.executor, interpreter="python"
        )

        if not wikis_loader.is_running():
            wikis_loader.start()

    def start(self, background=False):
        """

        kosmos 'j.servers.threebot.default.start()'

        :param background:
        :return:
        """

        if not background:

            self._zdb_start()
            self._sonic_start()

            openresty = self.openresty_server
            gedis = self.gedis_server
            rack = self.rack


            # add base actors and chatflows
            gedis.actors_add("%s/base_actors" % self._dirpath)
            gedis.chatbot.chatflows_load("%s/base_chatflows" % self._dirpath)

            # add gedis websocket server
            app = j.servers.gedis_websocket.default.app
            rack.websocket_server_add("websocket", 9999, app)

            # Question: why is this needed?
            dns = j.servers.dns.get_gevent_server("main", port=5354)  # for now high port
            rack.add("dns", dns)

            rack.add("gedis", gedis.gevent_server)

            rack.bottle_server_add(port=4443)
            # reverse proxies for gevent servers to issue a certificate from nginx
            websocket_reverse_proxy = openresty.reverseproxies.new(
                name="websocket", port_source=4444, proxy_type="websocket", port_dest=9999, ipaddr_dest="0.0.0.0"
            )
            websocket_reverse_proxy.configure()

            gedis_reverse_proxy = openresty.reverseproxies.new(
                name="gedis", port_source=8900, proxy_type="tcp", port_dest=8901, ipaddr_dest="0.0.0.0"
            )
            gedis_reverse_proxy.configure()

            bottle_reverse_proxy = openresty.reverseproxies.new(
                name="bottle", port_source=4442, proxy_type="http", port_dest=4443, ipaddr_dest="0.0.0.0"
            )
            bottle_reverse_proxy.configure()

            # add user added packages
            for package in j.tools.threebotpackage.find():
                package.start()

            openresty.start()
            rack.start()

        else:
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
