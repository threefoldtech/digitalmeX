from Jumpscale import j

JSBASE = j.application.JSBaseClass

# WIKI_CONFIG_TEMPLATE = "templates/WIKI_CONF_TEMPLATE.conf"
# WEBSITE_CONFIG_TEMPLATE = "templates/WEBSITE_CONF_TEMPLATE.conf"
# WEBSITE_STATIC_CONFIG_TEMPLATE = "templates/WEBSITE_STATIC_CONF_TEMPLATE.conf"
# OPEN_PUBLISH_REPO = "https://github.com/threefoldtech/OpenPublish"


from .OpenRestyServer import OpenRestyServer


class OpenRestyFactory(j.application.JSBaseConfigsClass):
    """
    Factory for openresty
    """

    __jslocation__ = "j.servers.openresty"
    _CHILDCLASS = OpenRestyServer

    def _init(self, **kwargs):
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.new(name="default")
        return self._default

    def build(self):
        j.builders.runtimes.lua.build()  # also gets the openresty

    def test(self):
        """
        kosmos 'j.servers.openresty.test()'
        :return:
        """

        self.build()

        openresty = self.default

        ws = openresty.websites.new(name="test", path="html", port=81)
        ws.configure()

        wiki = openresty.wikis.new(
            name="tfgrid", giturl="https://github.com/threefoldfoundation/info_grid", branch="development"
        )
        # will auto pull the content if not there yet

        rp = openresty.reverseproxies.new()

        # TODO: implement some reverse proxie tests
        # run 2 openresties, one at back on other port one at front
        assert False

        openresty.reload()

        openresty._log_info("can now go to http://localhost:81/index.html")
