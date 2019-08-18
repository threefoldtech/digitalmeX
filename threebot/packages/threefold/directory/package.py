from Jumpscale import j


class Package(j.application.ThreeBotPackageBase):
    def prepare(self):
        """
        is called at install time
        :return:
        """
        zdb_admin = j.clients.zdb.client_admin_get()
        # zdb_admin.reset()
        zdb_admin.namespace_new("tf_directory", secret="123456")
        zdb = j.clients.zdb.get(name="tf_directory", port=9900, secret_="123456")
        bcdb = j.data.bcdb.get(name="tf_directory", storclient=zdb)

    def start(self):
        """
        called when the 3bot starts
        :return:
        """

        bcdb = j.data.bcdb.get(name="tf_directory")

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
