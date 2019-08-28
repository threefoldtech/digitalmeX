from Jumpscale import j

from .app import App

JSConfigClient = j.application.JSBaseConfigClass


class FileManServer(JSConfigClient):
    _SCHEMATEXT = """
       @url =  jumpscale.servers.radicale
       name* = "default" (S)
       port = 6666 (I)
       """

    def start(self, background=False):
        if not background:
            rack = j.servers.rack.get()
            app = App(self._dirpath)()
            rack.bottle_server_add(name="fileman", port=self.port, app=app)
            rack.start()

    def install(self):
        j.builders.runtimes.python.pip_package_install("filetype")
