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

    def build(self):
        """
        will make sure to build lua and install lua-resty-auto-ssl (to automatically issue ssl certificates)
        :return:
        """
        j.builders.runtimes.lua.build()  # also gets the openresty
        j.builders.runtimes.lua.lua_rock_install("lua-resty-auto-ssl")
        # this is a hack shouldn't be done if the paths are correct see https://github.com/threefoldtech/jumpscaleX/pull/692
        j.sal.fs.copyDirTree("/sandbox/openresty/luarocks/bin/resty-auto-ssl/", "/bin", rsyncdelete=False)
        j.sal.unix.addSystemGroup("www")
        j.sal.unix.addSystemUser("www", "www")
        j.sal.fs.createDir("/etc/resty-auto-ssl")
        j.sal.fs.chown("/etc/resty-auto-ssl", "www", "www")
        j.sal.fs.chmod("/etc/resty-auto-ssl", 0o755)
        # Generate a self signed fallback certificate
        cmd = """
        openssl req -new -newkey rsa:2048 -days 3650 -nodes -x509 \
            -subj '/CN=sni-support-required-for-valid-ssl' \
            -keyout /etc/ssl/resty-auto-ssl-fallback.key \
            -out /etc/ssl/resty-auto-ssl-fallback.crt
        """
        j.tools.executor.local.execute(cmd)

    def test(self):
        """
        kosmos 'j.servers.openresty.test()'
        :return:
        """

        self.build()

        openresty = self.default
        openresty.install()

        ip_addr = "0.0.0.0"
        import os

        domain = os.environ.get("DOMAIN", "")
        ws = openresty.websites.new(name="test", location=ip_addr, path="html", port=8080)
        ws.configure()

        rp = openresty.reverseproxies.new(
            name="testrp", port_source=80, domain=domain, port_dest=8080, ipaddr_dest=ip_addr
        )
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
