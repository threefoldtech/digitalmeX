from Jumpscale import j

from .ZOSContainer import ZOSContainers
from .ZOSInstance import ZOSInstance


class ZOSVirtual(ZOSInstance):
    """
    is the host which runs a ZOS operating system

    is a Virtual Zero-OS running on a virtual service provider

    """

    def _init(self, **kwargs):
        pass
