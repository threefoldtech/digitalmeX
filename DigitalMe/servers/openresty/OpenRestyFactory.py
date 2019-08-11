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
            self._default = self.get(name="default")
        return self._default

    def install(self, reset=False):
        """
        kosmos 'j.servers.openresty.install(reset=True)'
        :param reset:
        :return:
        """
        if reset:
            j.sal.fs.remove("/sandbox/var/web")
        j.builders.web.openresty.install()
        j.builders.runtimes.lua.install()
        j.clients.git.pullGitRepo(url="https://github.com/threefoldtech/jumpscale_weblibs")

    def test(self, install=True):
        """
        kosmos 'j.servers.openresty.test(install=False)'
        :return:
        """
        if install:
            self.install()

        def corex():
            self._log_info("Now trying coreX")
            j.servers.corex.default.check()

            corex = j.servers.corex.default.client
            openresty = self.get(name="default", executor="corex", corex_client_name=corex.name)

            # openresty.install()

            ip_addr = "0.0.0.0"
            import os

            domain = os.environ.get("DOMAIN", "")

            ws = openresty.websites.new(name="test", location=ip_addr, path="html", port=8080)
            ws.configure()

            rp = openresty.reverseproxies.new(
                name="testrp", port_source=80, domain=domain, port_dest=8080, ipaddr_dest=ip_addr
            )
            rp.configure()
            openresty.start()

            website_response = j.clients.http.get("http://{}:8080".format(ip_addr))
            assert website_response == "<!DOCTYPE html>\n<html>\n<body>\n\nwelcome\n\n</body>\n</html>\n"
            self._log_info("[+] test website response OK")
            # test the reverse prosy port
            reverse_response = j.clients.http.get("http://{}:80".format(ip_addr))
            assert reverse_response == website_response
            self._log_info("[+] test reverse proxy response OK")

            self._log_info("can now go to http://localhost:8080/index.html")
            self._log_info("now closing")

            openresty.stop()

        def tmux():

            openresty = self.default
            openresty.install()

            ip_addr = "0.0.0.0"
            domain = os.environ.get("DOMAIN", "")
            ws = openresty.websites.new(name="test", domain=domain, location=ip_addr, path="html", port=8080)
            ws.configure()

            rp = openresty.reverseproxies.new(name="testrp", port_source=80, port_dest=8080, ipaddr_dest=ip_addr)
            rp.configure()

            if openresty.is_running():
                openresty.reload()
            else:
                openresty.start()

            # wiki = openresty.wikis.new(
            #     name="tfgrid", giturl="https://github.com/threefoldfoundation/info_grid", branch="development"
            # )

            website_response = j.clients.http.get("http://{}:8080".format(ip_addr))
            assert website_response == "<!DOCTYPE html>\n<html>\n<body>\n\nwelcome\n\n</body>\n</html>\n"
            self._log_info("[+] test website response OK")
            # test the reverse prosy port
            reverse_response = j.clients.http.get("http://{}:80".format(ip_addr))
            assert reverse_response == website_response
            self._log_info("[+] test reverse proxy response OK")

            self._log_info("can now go to http://localhost:8080/index.html")

            self._log_info("now closing")
            # openresty.stop()

            self._log_info("TEST OK")

        tmux()
        # corex()
