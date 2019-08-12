from .ThreebotServer import ThreeBotServer
from Jumpscale import j
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass


class ThreeBotServersFactory(j.application.JSBaseConfigsClass):
    """
    Factory for 3bots
    """

    __jslocation__ = "j.servers.threebot"
    _CHILDCLASS = ThreeBotServer

    def _init(self):
        self._default = None
        self.current = None

    @property
    def default(self):
        if not self._default:
            self._default = self.get("default")
        return self._default

    def install(self):
        j.builders.web.openresty.install()
        j.builders.runtimes.lua.install()
        j.builders.db.zdb.install()
        j.builders.apps.sonic.install()

    def bcdb_get(self, name, secret="", use_zdb=False):
        return self.default.bcdb_get(name, secret, use_zdb)

    def test(self, start=True):
        """

        kosmos 'j.servers.threebot.test(start=False)'
        kosmos 'j.servers.threebot.test()'
        :return:
        """
        if start:
            self.default.stop()
            self.default.start(background=True)

        # add an actor

        cl = j.clients.gedis.get(name="threebot")

        assert cl.ping()

        cl.actors.package_manager.package_add(
            "tf_directory",
            git_url="https://github.com/threefoldtech/digitalmeX/tree/development_jumpscale/threebot/packages/threefold/directory",
        )

        cl.actors.package_manager.package_add(
            "threebot_phonebook",
            git_url="https://github.com/threefoldtech/digitalmeX/tree/development_jumpscale/threebot/packages/threefold/phonebook",
        )

        cl.reload()

        r = cl.actors.farms.list()

        u = cl.actors.phonebook.register(name="kristof.gouna", email=None, pubkey="aaaaa", signature="bbbbb")

        j.shell()
