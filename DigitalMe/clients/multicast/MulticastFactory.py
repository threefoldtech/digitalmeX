

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
from .MulticastClient import MulticastClient

JSConfigBase = j.application.JSFactoryConfigsBaseClass


class MulticastFactory(JSConfigBase):
    def __init__(self):
        self.__jslocation__ = "j.clients.multicast"
        JSConfigBase.__init__(self, MulticastClient)

    def test_listen(self):
        """
        js_shell 'j.clients.multicast.test_listen()'
        """
        data = {}
        # data["group"]='ff15:7079:7468:6f6e:6465:6d6f:6d63:6173'
        data["port"] = 8123
        cl = self.get(data=data)
        print("listen")
        cl.listen()

    def test_send(self):
        """
        js_shell 'j.clients.multicast.test_send()'
        """
        data = {}
        data["group"] = "ff15:7079:7468:6f6e:6465:6d6f:6d63:6173"
        data["port"] = 8123
        cl = self.get(data=data)
        cl.send()
