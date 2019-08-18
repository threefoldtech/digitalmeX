from Jumpscale import j

from .ZOSContainer import ZOSContainers
from .ZOSInstance import ZOSInstance


class ZOSHostVirtualbox(ZOSInstance):
    """
    is the host which runs a ZOS operating system

    this one is a virtualbox host

    if allows to manage the virtualbox as well

    """

    @property
    def _SCHEMATEXT(self):
        j.shell()

    def _init(self, **kwargs):
        pass
