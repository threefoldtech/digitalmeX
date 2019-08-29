from Jumpscale import j

from .app import App

JSConfigClient = j.application.JSBaseConfigClass


class WebdavServer(JSConfigClient):
    _SCHEMATEXT = """
       @url =  jumpscale.servers.webdav
       name* = "default" (S)
       port = 6661 (I)
       """

    def start(self, background=False):
        self.install()
        if not background:
            rack = j.servers.rack.get()
            rack.webdav_server_add(name=self.name, path="/", port=self.port, webdavprovider=None)
            rack.bottle_server_add(name="fileman", port=self.port, app=app)
            rack.start()

    def install(self):
        j.builders.runtimes.python.pip_package_install("filetype")
