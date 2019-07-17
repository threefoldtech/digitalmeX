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

    def start(self, background=False):

        if not background:

            # j.clients.git.getContentPathFromURLorPath(OPEN_PUBLISH_REPO, pull=False)
            url = "https://github.com/threefoldtech/jumpscale_weblibs"
            weblibs_path = j.clients.git.getContentPathFromURLorPath(url, pull=True)
            j.sal.fs.symlink(
                "{}/static".format(weblibs_path),
                "{}/static/weblibs".format(self.open_publish_path),
                overwriteTarget=False,
            )

            zdb = j.servers.zdb.new("threebot", adminsecret_=self.adminsecret, executor=self.executor)
            zdb.start()

            # Start Sonic Server
            sonic_server = j.servers.sonic.default
            sonic_server.start()

            # is not the right way, need to use config classes but maybe ok for now
            j.tools.markdowndocs.sonic_client_set(sonic_server.default_client)

            rack = j.servers.rack.get()

            gedis = j.servers.gedis.get_gevent_server("main", port=8900)
            rack.add("gedis", gedis)

            # TODO, needs to be possible to run ssl and not but still use the same gedis backend, should not have to run 2x
            # gedis = j.servers.gedis.get_gevent_server("main_ssl", ssl=True, port=8901)
            # rack.add("gedis_ssl", gedis)

            gedis.actors_add("%s/base_actors" % self._dirpath)
            gedis.chatbot.chatflows_load("%s/base_chatflows" % self._dirpath)

            dns = j.servers.dns.get_gevent_server(port=5354)  # for now high port
            rack.add("dns", dns)

            rack.start()

        else:
            # the MONKEY PATCH STATEMENT IS NOT THE BEST, but prob required for now
            S = """
            from gevent import monkey
            monkey.patch_all(subprocess=False)
            from Jumpscale import j
            j.servers.rack._grack_server_start()
            """

            S = j.core.tools.text_replace(S, args)

            s = j.servers.startupcmd.new(name="threebot")
            s.cmd_start = S
            s.executor = self.executor
            s.interpreter = "python"
            s.timeout = 10
            s.ports = [8900, 8901]
            if s.is_running():
                s.stop()
            s.start()


class ThreeBotServers(j.application.JSBaseConfigsClass):
    _name = "servers"
    _CHILDCLASS = ThreeBotServer
