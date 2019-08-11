import json
from Jumpscale import j


JSBASE = j.application.JSBaseClass


class package:
    def __init__(self, package_url):

        self._path = j.clients.git.getContentPathFromURLorPath(package_url)
        self._path_package = "%s/package.py" % (self._path)

        if not j.sal.fs.exists(self._path_package):
            raise j.exceptions.Input("cannot find package.py in the package directory", data=package_url)

        self._package = j.tools.codeloader.load(obj_key="Package", path=self._path_package, reload=False)

        self.prepare = self._package.prepare
        self.start = self._package.start
        self.stop = self._package.stop
        self.delete = self._package.delete


class package_manager(JSBASE):
    """
    """

    def _init(self, gedis_server=None):
        assert gedis_server
        self._gedis_server = gedis_server

    def package_add(self, package_url):

        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        eval("install")()

    def package_prepare(self, package_url):
        path = j.clients.git.getContentPathFromURLorPath(package_url)
        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        # TODO: check if already installed or not
        eval("prepare")()

    def package_uninstall(self, package_url):
        path = j.clients.git.getContentPathFromURLorPath(package_url)
        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        eval("uninstall")()

    def package_update(self, package_url):
        path = j.clients.git.getContentPathFromURLorPath(package_url)
        with open(j.sal.fs.joinPaths(path, "package.py")) as f:
            self.content = f.read()
        exec(self.content)
        # TODO: check if already installed or not
        eval("update")()

    def work_get(self, sessionid):
        """
        ```in
        sessionid = "" (S)
        ```
        """
        res = self.chatbot.session_work_get(sessionid)
        return json.dumps(res)

    def work_report(self, sessionid, result):
        """
        ```in
        sessionid = "" (S)
        result = "" (S)
        ```
        """
        self.chatbot.session_work_set(sessionid, result)
        return

    def session_alive(self, sessionid, schema_out):
        # TODO:*1 check if greenlet is alive
        pass

    def ping(self):
        return "PONG"

    def session_new(self, topic):
        """
        ```in
        topic = "" (S)
        ```
        """
        return json.dumps(self.chatbot.session_new(topic))
