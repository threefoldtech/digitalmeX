from Jumpscale import j


# class Package(j.application.ThreeBotPackageBase):
class Package:
    def prepare(self, gedis_server=None, package_root=None):
        """
        is called at install time
        :return:
        """

        zdb_admin = j.clients.zdb.client_admin_get()

        zdb_admin.reset()

        zdb_admin.namespace_new("directory", secret="123456")

        schema_path = j.sal.fs.joinPaths(package_root, "schemas.toml")
        schema_content = j.sal.fs.readFile(schema_path)
        j.data.schema.add_from_text(schema_content)

        zdb = j.clients.zdb.get("threebot", port=9900, nsname="directory", secret_="123456")
        #
        # zdb.set("a")
        # assert zdb.get(0) == b"a"
        # zdb.set("b", 0)
        # assert zdb.get(0) == b"b"
        # zdb.delete(0)

        bcdb = j.data.bcdb.get("directory", storclient=zdb)
        bcdb.model_get_from_schema(schema_content)

        actor_path = j.sal.fs.joinPaths(package_root, "actors")
        gedis_server.actors_add(actor_path)

    def start(self):
        """
        called when the 3bot starts
        :return:
        """
        pass

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
