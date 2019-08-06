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
        self.content = ""

    @property
    def gedis_server(self):
        if not self._gedis_server:
            self._gedis_server = j.servers.gedis.get("main", port=8900)
        return self._gedis_server

    def start(self, background=False):

        if not background:
            zdb = j.servers.zdb.new("threebot", adminsecret_=self.adminsecret_, executor=self.executor)
            zdb.start()

            rack = j.servers.rack.get()

            # TODO, needs to be possible to run ssl and not but still use the same gedis backend, should not have to run 2x
            # gedis = j.servers.gedis.get("main_ssl", ssl=True, port=8901)
            # rack.add("gedis_ssl", gedis)

            openresty = j.servers.openresty.get("threebot", executor=self.executor)
            j.servers.openresty.build()
            wikis_load_cmd = """
from Jumpscale import j
j.tools.markdowndocs.load_wikis()
            """
            wikis_loader = j.servers.startupcmd.get(
                "wikis_loader", cmd_start=wikis_load_cmd, timeout=60 * 60, executor=self.executor, interpreter="python"
            )
            if not wikis_loader.is_running():
                wikis_loader.start()
            openresty.install()
            openresty.start()
            self._gedis_server = j.servers.gedis.get("main", port=8900)

            self._gedis_server.actors_add("%s/base_actors" % self._dirpath)
            self._gedis_server.chatbot.chatflows_load("%s/base_chatflows" % self._dirpath)
            self.package_add(os.path.join(os.path.dirname(__file__)))
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
            startup.timeout = 5 * 60
            startup.ports = [8900, 4444, 8090]
            if startup.is_running():
                startup.stop()
            startup.start()

    def auto_update(self):
        while True:
            self._log_info("Reload for docsites done")
            gevent.sleep(300)

    def package_add(self, package_url):
        path = j.clients.git.getContentPathFromURLorPath(package_url)

        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        eval("install")()

    def package_perpare(self, package_url):
        path = j.clients.git.getContentPathFromURLorPath(package_url)
        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        # TODO: check if already installed or not
        eval("prepare")()

    def package_uninstall(self, package_url):
        path = j.clients.git.getContentPathFromURLorPath(package_url)
        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        eval("uninstall")()

    def package_update(self, package_url):
        path = j.clients.git.getContentPathFromURLorPath(package_url)
        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        # TODO: check if already installed or not
        eval("update")()
