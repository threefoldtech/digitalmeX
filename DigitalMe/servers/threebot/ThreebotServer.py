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
        self._gedis_server = None
        self.dns_server = None

    @property
    def gedis_server(self):
        if not self._gedis_server:
            self._gedis_server = j.servers.gedis.get("main", port=8900)
        return self._gedis_server

    def start(self, background=False):

        if not background:
            zdb = j.servers.zdb.new("threebot", adminsecret_=self.adminsecret_, executor=self.executor)
            zdb.start()
            # Start Sonic Server
            sonic_server = j.servers.sonic.default
            sonic_server.start()

            # is not the right way, need to use config classes but maybe ok for now
            j.tools.markdowndocs.sonic_client_set(sonic_server.default_client)

            rack = j.servers.rack.get()

            app = j.servers.gedis_websocket.default.app
            rack.websocket_server_add("websocket", 4444, app)

            # TODO, needs to be possible to run ssl and not but still use the same gedis backend, should not have to run 2x
            # gedis = j.servers.gedis.get("main_ssl", ssl=True, port=8901)
            # rack.add("gedis_ssl", gedis)

            dns = j.servers.dns.get_gevent_server("main", port=5354)  # for now high port
            rack.add("dns", dns)

            openresty = j.servers.openresty.get("threebot", executor=self.executor)
            j.servers.openresty.build()
            url = "https://github.com/threefoldfoundation/info_grid/tree/development/docs"
            tf_grid = j.tools.markdowndocs.load(url, name="grid")
            tf_grid.write()
            url = "https://github.com/threefoldfoundation/info_foundation/tree/development/docs"
            tf_foundation = j.tools.markdowndocs.load(url, name="foundation")
            tf_foundation.write()

            openresty.start()
            self._gedis_server = j.servers.gedis.get("main", port=8900)

            self._gedis_server.actors_add("%s/base_actors" % self._dirpath)
            self._gedis_server.chatbot.chatflows_load("%s/base_chatflows" % self._dirpath)

            rack.add("gedis", self._gedis_server.gedis_server)
            rack.start()

        else:
            # the MONKEY PATCH STATEMENT IS NOT THE BEST, but prob required for now
            cmd_start = """
from gevent import monkey
monkey.patch_all(subprocess=False)
from Jumpscale import j
j.servers.threebot.get("{name}", executor='{executor}').start(background=False)
            """.format(
                name=self.name, executor=self.executor
            )

            startup = j.servers.startupcmd.get(name="threebot_{}".format(self.name))
            startup.cmd_start = cmd_start
            startup.executor = self.executor
            startup.interpreter = "python"
            startup.timeout = 10
            startup.ports = [8900, 4444, 5354, 1491]
            if startup.is_running():
                startup.stop()
            startup.start()

    def auto_update(self):
        while True:
            self._log_info("Reload for docsites done")
            gevent.sleep(300)
