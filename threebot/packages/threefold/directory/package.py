from Jumpscale import j


class Package(j.application.ThreeBotPackageBase):
    def prepare(self):
        """
        is called at install time
        :return:
        """
        pass

    def start(self):
        """
        called when the 3bot starts
        :return:
        """

        def storclient():
            zdb_admin = j.clients.zdb.client_admin_get()
            # zdb_admin.reset()
            zdb_admin.namespace_new("directory", secret="123456")
            zdb = j.clients.zdb.get("threebot", port=9900, nsname="directory", secret_="123456")

            return None  # to deal with TEMP BUG #TODO:
            return zdb

        bcdb = j.data.bcdb.get("directory", storclient=storclient())
        bcdb.models_add(path=self.package_root + "/models")

        self.gedis_server.actors_add(j.sal.fs.joinPaths(self.package_root, "actors"))

        j.shell()

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
