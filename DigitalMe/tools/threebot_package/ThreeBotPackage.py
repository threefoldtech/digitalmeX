from Jumpscale import j

JSConfigBase = j.application.JSBaseConfigClass


class ThreeBotPackage(JSConfigBase):
    _SCHEMATEXT = """
        @url = jumpscale.threebot.package.1
        name* = "main"        
        giturl = "" (S)  #if empty then local
        path = ""
        """

    def _init(self, **kwargs):
        if self.giturl:
            self._path = j.clients.git.getContentPathFromURLorPath(self.giturl)
        else:
            self._path = self.path

        self._path_package = "%s/package.py" % (self._path)

        if not j.sal.fs.exists(self._path_package):
            raise j.exceptions.Input("cannot find package.py in the package directory", data=package_url)

        self._package = j.tools.codeloader.load(obj_key="Package", path=self._path_package, reload=False)

        self.prepare = self._package.prepare
        self.start = self._package.start
        self.stop = self._package.stop
        self.delete = self._package.delete
