from Jumpscale import j

from .ZosNodes.ZOSHostOVH import ZOSHostOVH
from .ZosNodes.ZOSHostVirtualbox import ZOSHostVirtualbox
from .ZosNodes.ZOSTFNode import ZOSTFNode
from .ZosNodes.ZOSVirtual import ZOSVirtual


class ZOSInstanceFactory(j.application.JSFactoryConfigsBaseClass):
    """
    hosts different implementation of zos hosts
    its a factory class to allow you to get the right type of ZOS host or virtual ZOS

    """

    _CHILDCLASSES = [ZOSHostVirtualbox, ZOSHostOVH, ZOSTFNode, ZOSVirtual]
