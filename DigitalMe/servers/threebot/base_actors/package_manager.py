import json
from Jumpscale import j


class package_manager(j.application.ThreeBotActorBase):
    def _init(self, gedis_server=None):
        assert gedis_server
        self._gedis_server = gedis_server

    def package_add(self, name=None, git_url=None, path=None):
        """
        ```in
        name = ""
        git_url = ""
        path = ""
        ```
        """

        if name is None or name == "":
            raise j.exceptions.Input("actor name cannot be None or empty")

        if git_url and path:
            raise j.exceptions.Input("add can only be done by git_url or name but not both")

        assert j.servers.threebot.current
        threebotserver_name = j.servers.threebot.current.name

        if git_url:

            package = j.tools.threebotpackage.get(name=name, giturl=git_url, threebotserver_name=threebotserver_name)
        elif path:
            package = j.tools.threebotpackage.get(name=name, path=path, threebotserver_name=threebotserver_name)
        else:
            raise j.exceptions.Input("need to have git_url or path to package")

        package.save()
        package.prepare()
        package.start()

    def package_delete(self, name):
        """
        ```in
        name = ""
        ```
        """
        if not j.tools.threebotpackage.exists(name):
            return

        package = j.tools.threebotpackage.get(name)
        package.uninstall()
        package.delete()

    def package_stop(self, name):
        """
        ```in
        name = ""
        ```
        """
        if not j.tools.threebotpackage.exists(name):
            raise j.exceptions.NotFound("package not found", data={"name": name})

        package = j.tools.threebotpackage.get(name)
        package.stop()

    def package_start(self, name):
        """
        ```in
        name = ""
        ```
        """
        if not j.tools.threebotpackage.exists(name):
            raise j.exceptions.NotFound("package not found", data={"name": name})

        package = j.tools.threebotpackage.get(name)
        package.start()
