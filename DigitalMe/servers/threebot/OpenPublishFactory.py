from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass


class OpenPublishFactory(JSConfigs):
    """
    Open Publish factory
    """

    __jslocation__ = "j.servers.threebot"
    _CHILDCLASS = OpenPublish

    def __init__(self):
        JSConfigs.__init__(self)
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.get("default")
        return self._default

    def bcdb_get(self, name, secret="", use_zdb=False):
        return self.default.bcdb_get(name, secret, use_zdb)

    def start(self, background=True):
        """
        kosmos 'j.servers.threebot.start()'
        """
        if background:
            cmd = "kosmos 'j.servers.threebot.start(background=False)'"
            j.servers.tmux.execute(cmd, window="Open Publish", pane="main", reset=False)
            self._log_info("waiting for gedis to start on port {}".format(self.default.gedis.port))
            res = j.sal.nettools.waitConnectionTest("localhost", self.default.gedis_server.port, timeoutTotal=120)
            if not res:
                raise RuntimeError("Failed to start Open Publish")
            self._log_info("Open Publish framework started")
        else:
            self.default.servers_start()
