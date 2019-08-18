from Jumpscale import j

from .ZOSContainer import ZOSContainers


class ZOSInstance(j.application.JSFactoryConfigsBaseClass):
    """
    is the host which runs a ZOS operating system
    TODO: maybe should call this ZOSHost?
    """

    _SCHEMATEXT = """
    @url = jumpscale.clients.zoscmd.zosnode.1
    name* = ""
    zos_addr = "127.0.0.1" (S)
    zos_port = 6379 (I)
    local_addr = "127.0.0.1" (S)  #when a private network is available, e.g. in local VirtualBox, can be used to create e.g. ssh connections locally
    jwt = "" (S)
    type = "physical, ovh, ovc, packetnet, virtualbox" (E)   
    description = ""
    
    """

    _CHILDCLASSES = [ZOSContainers]

    def _init(self, **kwargs):
        self._zos_client_ = None

    @property
    def _zos_client(self):
        """
        """
        if self._zos_client_ is None:
            j.shell()

    # def zos_container_get(self,name="test"):
    #     if name not in self.zos_containers:
    #         zc = ZOSContainer(name=name)
    #         zc.zos_node = self
    #         self.zos_containers[name] = zc
    #     return self.zos_containers[name]
    #
    # def zos_virtual_get(self,name="test"):
    #     """
    #     returns a VM which has a ZOS virtual machine
    #     only works when zosnode is "physical","ovh" or "packetnet"
    #     :param name:
    #     :return:
    #     """
    #     if self.type not in ["physical","ovh","packetnet"]:
    #         raise j.exceptions.Base("platform '%s' not supported"%self.type)
    #     if name not in self.zos_virtual:
    #         zc = ZOSVirtual(name=name)
    #         zc.zos_node = self
    #         self.zos_virtual[name] = zc
    #     return self.zos_virtual[name]

    def __str__(self):
        return "zero-os: %-14s %-25s:%-4s" % (self.name, self.addr, self.port)

    __repr__ = __str__
