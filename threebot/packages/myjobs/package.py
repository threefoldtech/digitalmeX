from Jumpscale import j


class Package(j.application.ThreeBotPackageBase):
    def prepare(self):
        """
        is called at install time
        :return:
        """

        html_root = j.sal.fs.joinPaths(self.package_root, "html")

        # should add myjobs.dev to /etc/hosts to test
        website = self.openresty.websites.new(
            name="myjobs", port=3800, location="myjobs", domain="myjobs.dev", path=html_root
        )
        website.configure()

        # FIXME: need to update this hardcoded path
        j.sal.fs.symlink(html_root, f"/sandbox/var/web/threebot/html/myjobs")

    def start(self):
        """
        called when the 3bot starts
        :return:
        """
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
        pass
