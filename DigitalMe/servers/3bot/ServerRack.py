from Jumpscale import j
import os
import sys
from importlib import import_module

JSBASE = j.application.JSBaseClass
from gevent import spawn
from gevent import monkey
import gevent
from gevent import event


class ServerRack(JSBASE):
    """
    is a group of gedis servers in a virtual rack
    """

    def __init__(self):
        JSBASE.__init__(self)
        self.servers = {}
        self._monkeypatch_done = False

    def add(self, name, server):
        """
        add a gevent server e.g

        - gedis_server = j.servers.gedis.geventservers_get("test")
        - web_server = j.servers.web.geventserver_get("test")

        can then add them

        REMARK: make sure that subprocesses are run before adding gevent servers

        """
        self._monkeypatch()
        self.servers[name] = server

    def _monkeypatch(self):
        if not self._monkeypatch_done:
            monkey.patch_all(subprocess=False)
            self._monkeypatch_done = True

    def _nomonkeypatch_check(self):
        if self._monkeypatch_done:
            raise RuntimeError(
                "cannot start workers because gevent has been inited already, make sure you do gevent later"
            )

    def filemonitor_start(self, gedis_instance_name=None, subprocess=True):
        """
        @param gedis_instance_name: gedis instance name that will be monitored

        js_shell 'j.servers.digitalme.filemonitor_start("test",subprocess=False)'

        """
        self._nomonkeypatch_check()
        from .FileSystemMonitor import monitor_changes_subprocess, monitor_changes_parent

        if subprocess:
            self.filemonitor = monitor_changes_parent(gedis_instance_name=gedis_instance_name)
        else:
            monitor_changes_subprocess(gedis_instance_name=gedis_instance_name)

    def webdav(self):
        from wsgidav.fs_dav_provider import FilesystemProvider
        from wsgidav.version import __version__
        from wsgidav.wsgidav_app import DEFAULT_CONFIG, WsgiDAVApp
        from gevent.pywsgi import WSGIServer

        provider = FilesystemProvider(args.path)
        config = DEFAULT_CONFIG.copy()
        config.update(
            {
                "provider_mapping": {"/": provider},
                "port": 8887,
                "host": "0.0.0.0",
                "verbose": True,
                "propsmanager": True,
                "locksmanager": False,
            }
        )
        print("config:")
        print(config)
        app = WsgiDAVApp(config)

        server = WSGIServer((args.host, args.port), application=app)
        server.set_environ({"SERVER_SOFTWARE": "WsgiDAV/{} ".format(__version__) + server.base_env["SERVER_SOFTWARE"]})
        print("Running {} on http://{}:{}".format(server.get_environ()["SERVER_SOFTWARE"], args.host, args.port))

    def start(self):
        self._monkeypatch()
        started = []
        try:
            for key, server in self.servers.items():
                server.start()
                started.append(server)
                name = getattr(server, "name", None) or server.__class__.__name__ or "Server"
                self._log_info("%s started on %s" % (name, server.address))
        except:
            self.stop(started)
            raise

        forever = event.Event()
        try:
            forever.wait()
        except KeyboardInterrupt:
            self.stop()

    def stop(self, servers=None):
        self._log_info("stopping server rack")
        if servers is None:
            servers = [item[1] for item in self.servers.items()]
        for server in servers:
            try:
                server.stop()
            except:
                if hasattr(server, "loop"):  # gevent >= 1.0
                    server.loop.handle_error(server.stop, *sys.exc_info())
                else:  # gevent <= 0.13
                    import traceback

                    traceback.print_exc()
