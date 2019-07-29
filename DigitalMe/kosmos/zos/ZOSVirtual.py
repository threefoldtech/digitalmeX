

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


class ZOSVirtual(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.clients.zoscmd.zosvirtual.1
    name = "" (S)
    ssh_addr = "127.0.0.1" (S)
    ssh_port = 22 (S)
    zos_addr = "127.0.0.1" (S)
    zos_port = 6379 (I)
    secret = "" (S)    
    """

    def _init(self, **kwargs):
        self.ZOSNode = None  # links to the ZOSNode which hosts this ZOSContainer

    @property
    def zos_client(self):
        """
        return zos protocol client
        :return:
        """
        pass
        # implement caching at client side

    def ssh_client(self):
        """

        :return: ssh client to this container
        """
        pass
        # implement caching at client side

    def __str__(self):
        return "zoscontainer:%-14s %-25s:%-4s" % (self.name, self.addr, self.port)

    __repr__ = __str__


# REMARK: create an SSH connection to the ZOS node, can only be done when virtual


# IMPLEMENT START/....
