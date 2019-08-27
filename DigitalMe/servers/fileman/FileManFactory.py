from Jumpscale import j

from .FileManServer import FileManServer

JSConfigs = j.application.JSBaseConfigsClass


class FileManFactory(JSConfigs):

    __jslocation__ = "j.servers.fileman"
    _CHILDCLASS = FileManServer

    def _init(self):
        self._logger_enable()

    def __init__(self):
        JSConfigs.__init__(self)
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.get("default")
        return self._default
