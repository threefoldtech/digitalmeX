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

        ip_addr = "0.0.0.0"
        ws = self.websites.new(name="test", location=ip_addr, path="html", port=8080)
        ws.configure()

        # wiki = openresty.wikis.new(
        #     name="tfgrid", giturl="https://github.com/threefoldfoundation/info_grid", branch="development"
        # )

        rp = self.reverseproxies.new(name="testrp", port_source=88, port_dest=8080, ipaddr_dest=ip_addr)
        rp.configure()

        # wiki = self.wikis.new(
        #     name="tfgrid", giturl="{}/examples/wiki".format(self._dirpath), branch="development", port=8088
        # )
        # wiki.update()

        openresty.reload()

        openresty._log_info("can now go to http://localhost:81/index.html")

        # TODO: we have a client for http in JSX use that one please
        import requests

        website_response = requests.get("http://{}:8080".format(ip_addr)).text
        assert website_response == "<!DOCTYPE html>\n<html>\n<body>\n\nwelcome\n\n</body>\n</html>\n"
        self._log_info("[+] test website response OK")
        # test the reverse prosy port
        reverse_response = requests.get("http://{}:88".format(ip_addr)).text
        assert reverse_response == website_response
        self._log_info("[+] test reverse proxy response OK")

        self._log_info("can now go to http://localhost:81/index.html")
