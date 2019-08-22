from Jumpscale import j


class Wiki:
    def __init__(self, name, url):
        self.name = name
        self.url = url
        # TODO: use the myjobs, wiki per wiki

    def load(self, name, url):
        a = j.tools.markdowndocs.load(url=url, name=name)
        a.write()


class Wikis:
    def add(self, name, url):
        self.__dict__[name] = Wiki(name=name, url=url)


class Package(j.application.ThreeBotPackageBase):
    def _init(self, **kwargs):
        self.branch = "development"

    def load(self, url):

        self.wikis = Wikis()
        self.wikis.add("tf_tokens", "https://github.com/threefoldfoundation/info_tokens/tree/%s/docs" % self.branch)
        self.wikis.add(
            "tf_foundation", "https://github.com/threefoldfoundation/info_foundation/tree/%s/docs" % self.branch
        )
        self.wikis.add("tf_grid", "https://github.com/threefoldfoundation/info_grid/tree/%s/docs" % self.branch)
        self.wikis.add("bettertoken", "https://github.com/BetterToken/info_bettertoken/tree/%s/docs" % self.branch)
        self.wikis.add("harvested", "https://github.com/harvested-io/info_harvested.io/tree/%s/docs" % self.branch)
        self.wikis.add(
            "freeflowevents", "https://github.com/freeflownation/info_freeflowevents/tree/%s/docs" % self.branch
        )

    def prepare(self):
        """
        is called at install time
        :return:
        """

        bcdb = self.package.threebot_server.bcdb_get("wiki")
        self.load()

        #
        # wikis_load_cmd = """
        # from Jumpscale import j
        # j.tools.markdowndocs.load_wikis()
        # """
        # wikis_loader = j.servers.startupcmd.get(
        #     "wikis_loader", cmd_start=wikis_load_cmd, timeout=60 * 60, executor=self.executor, interpreter="python"
        # )
        #
        # if not wikis_loader.is_running():
        #     wikis_loader.start()

    def start(self):
        """
        called when the 3bot starts
        :return:
        """

        bcdb = j.data.bcdb.get("threebot_phonebook")

        bcdb.models_add(path=self.package_root + "/models")

        self.gedis_server.actors_add(j.sal.fs.joinPaths(self.package_root, "actors"))

    def stop(self):
        """
        called when the 3bot stops
        :return:
        """
        pass

    def uninstall(self):
        """
        called when the package is no longer needed and will be removed from the threebot
        :return:
        """
        # TODO: clean up bcdb ?
        pass
