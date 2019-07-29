

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
from .GunClient import GunClient

JSConfigBase = j.application.JSFactoryConfigsBaseClass

ALLOWED_TYPES = {"gun": GunClient}  # available clients, add to this if a new client is added


class GedisBackendClientFactory(JSConfigBase):
    def __init__(self):
        self.__jslocation__ = "j.clients.gedis_backend"
        JSConfigBase.__init__(self, GunClient)

    def get(self, instance="main", data=None, create=True, die=True, interactive=True, type="gun"):
        if data is None:
            data = {}
        if not create and instance not in self.list():
            if die:
                raise RuntimeError("could not find instance:%s" % (instance))
            else:
                return None
        if type not in ALLOWED_TYPES:
            raise RuntimeError("Specified type not allowed")
        return ALLOWED_TYPES[type](instance=instance, data=data, interactive=interactive, parent=self)
