from .ReverseProxy import ReverseProxies
from .Wiki import Wikis
from .Website import Websites
from Jumpscale import j

JSBASE = j.application.JSBaseClass

# WIKI_CONFIG_TEMPLATE = "templates/WIKI_CONF_TEMPLATE.conf"
# WEBSITE_CONFIG_TEMPLATE = "templates/WEBSITE_CONF_TEMPLATE.conf"
# WEBSITE_STATIC_CONFIG_TEMPLATE = "templates/WEBSITE_STATIC_CONF_TEMPLATE.conf"
# OPEN_PUBLISH_REPO = "https://github.com/threefoldtech/OpenPublish"


class OpenRestyServer(j.application.JSBaseConfigsConfigFactoryClass):
    """
    Factory for openresty
    """

    _CHILDCLASSES = [Websites, Wikis, ReverseProxies]
    _SCHEMATEXT = """
           @url =  jumpscale.sonic.server.1
           name* = "default" (S)
           host = "127.0.0.1" (S)
           port = 80 (I)
           port_ssl = 443 (I)
           status = init,installed,ok (E)
           executor = tmux,corex (E)
           interpreter = "bash,jumpscale,direct,python" (E)  #direct means we will not put in bash script
           daemon = true (b)
           hardkill = false (b)
           state = "init,running,error,stopped,stopping,down,notfound" (E)
           corex_client_name = "default" (S)
           corex_id = (S)
           error = "" (S)
           time_start = (T)
           time_refresh = (T)
           time_stop = (T)
           """

    def _init(self, **kwargs):
        self._cmd = None
        self._web_path = "/sandbox/var/web/%s" % self.name
        j.sal.fs.createDir(self._web_path)

        self.executor = "tmux"

        if self.status == "INIT":
            self.install()

    def install(self):

        # get weblib
        url = "https://github.com/threefoldtech/jumpscale_weblibs"
        weblibs_path = j.clients.git.getContentPathFromURLorPath(url, pull=True)
        j.sal.fs.symlink("%s/static" % weblibs_path, "{}/static/weblibs".format(self._web_path), overwriteTarget=True)

        # copy the templates to the right location
        j.sal.fs.copyDirTree("%s/web_resources/" % self._dirpath, self._web_path)
        # link individual files & create a directory TODO:*1
        lualib_dir = "/sandbox/openresty/lualib"
        if not j.sal.fs.exists(lualib_dir):
            j.sal.fs.createDir(lualib_dir)
        j.sal.fs.copyFile("%s/web_resources/lualib/redis.lua" % self._dirpath, "/sandbox/openresty/lualib/redis.lua")
        j.sal.fs.copyFile(
            "%s/web_resources/lualib/websocket.lua" % self._dirpath, "/sandbox/openresty/lualib/websocket.lua"
        )
        self.status = "installed"

        self.save()

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
                ports=[self.port, self.port_ssl],
                process_strings_regex="^nginx",
                executor=self.executor,
            )
        return self._cmd

    def start(self, reset=False):
        """
        kosmos 'j.servers.openresty.start(reset=True)'
        kosmos 'j.servers.openresty.start(reset=False)'
        :return:
        """
        # compile all 1 time to lua, can do this at each start
        j.sal.process.execute("cd %s;moonc ." % self._web_path)
        from pudb import set_trace

        set_trace()
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

    def is_running(self):
        """
        :return:
        """
        self.startup_cmd.is_running()

    def reload(self):
        """
        :return:
        """
        cmd = "cd  %s;lapis build" % self._web_path
        j.sal.process.execute(cmd)
