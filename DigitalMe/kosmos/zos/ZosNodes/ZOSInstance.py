

# Copyright (C) 2019 :  TF TECH NV in Belgium see https://www.threefold.tech/
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.


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
    #         raise RuntimeError("platform '%s' not supported"%self.type)
    #     if name not in self.zos_virtual:
    #         zc = ZOSVirtual(name=name)
    #         zc.zos_node = self
    #         self.zos_virtual[name] = zc
    #     return self.zos_virtual[name]

    def __str__(self):
        return "zero-os: %-14s %-25s:%-4s" % (self.name, self.addr, self.port)

    __repr__ = __str__
