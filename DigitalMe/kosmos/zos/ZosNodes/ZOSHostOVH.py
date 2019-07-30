from Jumpscale import j

from .ZOSContainer import ZOSContainers
from .ZOSInstance import ZOSInstance


class ZOSHostOVH(ZOSInstance):
    """
    is the host which runs a ZOS operating system

    this one is an OVH host (is a service provider doing dedicated server hosting

    """

    def _init(self, **kwargs):
        pass
