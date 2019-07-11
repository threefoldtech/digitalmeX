from Jumpscale import j

JSBASE = j.application.JSBaseClass

# WIKI_CONFIG_TEMPLATE = "templates/WIKI_CONF_TEMPLATE.conf"
# WEBSITE_CONFIG_TEMPLATE = "templates/WEBSITE_CONF_TEMPLATE.conf"
# WEBSITE_STATIC_CONFIG_TEMPLATE = "templates/WEBSITE_STATIC_CONF_TEMPLATE.conf"
# OPEN_PUBLISH_REPO = "https://github.com/threefoldtech/OpenPublish"

from .Website import Websites
from .Wiki import Wikis
from .ReverseProxies import ReverseProxies


class OpenRestyFactory(j.application.JSBaseConfigsFactoryClass):
    """
    Factory for openresty
    """

    __jslocation__ = "j.servers.openresty"
    _CHILDCLASSES = [Websites, Wikis, ReverseProxies]

    def _init(self, **kwargs):
        self._cmd = None
        self._web_path = "/sandbox/var/web"
        self.executor = None

    def install(self):

        # copy the templates to the right location
        j.sal.fs.copyDirTree("%s/web_resources/" % self._dirpath, self._web_path)
        # link individual files & create a directory TODO:*1

        # get weblib
        url = "https://github.com/threefoldtech/jumpscale_weblibs"
        weblibs_path = j.clients.git.getContentPathFromURLorPath(url, pull=False)
        j.sal.fs.symlink("%s/static" % weblibs_path, "{}/static/weblibs".format(self._web_path), overwriteTarget=True)

    @property
    def startup_cmd(self):
        if not self._cmd:
            # Start Lapis Server
            self._log_info("Starting Lapis Server")
            cmd = "lapis server"
            self._cmd = j.servers.startupcmd.get(
                name="lapis",
                cmd_start=cmd,
                path=self._web_path,
                ports=[80, 443],
                process_strings_regex="^nginx",
                executor=self.executor,
            )
        return self._cmd

    def start(self, reset=False, executor="tmux"):
        """
        kosmos 'j.servers.openresty.start(reset=True)'
        kosmos 'j.servers.openresty.start(reset=False)'
        :return:
        """
        self.executor = executor
        self.install()
        # compile all 1 time to lua, can do this at each start
        j.sal.process.execute("cd %s;moonc ." % self._web_path)
        if reset:
            self.startup_cmd.stop()
        if self.startup_cmd.is_running():
            self.reload()
        else:
            self.startup_cmd.start()

    def stop(self):
        """
        kosmos 'j.servers.openresty.stop()'
        :return:
        """
        self.startup_cmd.stop()

    def reload(self):
        """
        :return:
        """
        cmd = "cd  %s;lapis build" % self._web_path
        j.sal.process.execute(cmd)

    def test(self):
        """
        kosmos 'j.servers.openresty.test()'
        :return:
        """

        ws = self.websites.new(name="test", path="html", port=81)
        ws.configure()

        wiki = self.wikis.new(
            name="tfgrid", giturl="https://github.com/threefoldfoundation/info_grid", branch="development"
        )
        # will auto pull the content if not there yet

        rp = self.reverseproxies.new()

        self.reload()

        self._log_info("can now go to http://localhost:81/index.html")
