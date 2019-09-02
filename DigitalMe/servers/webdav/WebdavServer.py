from Jumpscale import j

from wsgidav.wsgidav_app import WsgiDAVApp
from gevent.pywsgi import WSGIServer
from wsgidav.debug_filter import WsgiDavDebugFilter
from wsgidav.dir_browser import WsgiDavDirBrowser
from wsgidav.error_printer import ErrorPrinter
from wsgidav.http_authenticator import HTTPAuthenticator
from wsgidav.request_resolver import RequestResolver

from .provider import BCDBFSProvider
# from Jumpscale.data.bcdb.connectors.webdav.BCDBFSProvider import BCDBFSProvider
JSConfigClient = j.application.JSBaseConfigClass


class WebdavServer(JSConfigClient):
    _SCHEMATEXT = """
       @url =  jumpscale.servers.webdav
       name* = "default" (S)
       port = 6661 (I)
       """

    _app = None

    def get_app(self, name="webdav", path="/", port=6661, user_mapping={}, debug=False):
        if not self._app:

            # def addUser(realmName, user, password, description, roles=[]):
            #     realmName = "/" + realmName.strip(r"\/")
            #     userDict = user_mapping.setdefault(realmName, {}).setdefault(user, {})
            #     userDict["password"] = password
            #     userDict["description"] = description
            #     userDict["roles"] = roles
            # if user_mapping == {}:
            #     addUser("", "root", "root", "")

            if not j.data.bcdb.exists('fs'):
                j.data.bcdb.new('fs')

            config = {
                "host": "0.0.0.0",
                "port": port,
                "provider_mapping": {"/": BCDBFSProvider(path)},
                "verbose": 5,
                "middleware_stack": [
                    WsgiDavDebugFilter,
                    ErrorPrinter,
                    HTTPAuthenticator,
                    WsgiDavDirBrowser,  # configured under dir_browser option (see below)
                    RequestResolver,  # this must be the last middleware item
                ],
                "error_printer": {"catch_all": True},  # False,
                "enable_loggers": ['wsgidav'],
                "simple_dc": {"user_mapping": user_mapping or {"*": True}},
            }

            if debug:
                config['middleware_stack'].pop(0)
                config['middleware_stack'].pop(0)

            self._app = WsgiDAVApp(config)
            self._app.debug = True

        return self._app

    def start(self, background=False, debug=False):
        self.install()
        if not background:
            rack = j.servers.rack.get()
            server = WSGIServer(("0.0.0.0", self.port), application=self.get_app(debug=debug))
            rack.add(name=self.name, server=server)
            rack.start()

    def install(self):
        j.builders.runtimes.python.pip_package_install("filetype")
