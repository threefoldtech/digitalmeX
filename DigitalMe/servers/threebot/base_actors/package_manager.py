import json
from Jumpscale import j


class package_manager(j.application.ThreeBotActorBase):
    """
    """

    def package_add(self, name=None, git_url=None, path=None):
        """
        ```in
        name = ""
        git_url = ""
        path = ""
        ```
        """
        j.shell()

    def package_delete(self, name):
        """
        ```in
        name = ""
        ```
        """
        j.shell()

    def package_stop(self, name):
        """
        ```in
        name = ""
        ```
        """
        j.shell()

    def package_start(self, name):
        """
        ```in
        name = ""
        ```
        """
        j.shell()
