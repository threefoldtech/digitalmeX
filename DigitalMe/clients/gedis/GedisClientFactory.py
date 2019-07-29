

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

from .GedisClient import GedisClient

JSConfigBase = j.application.JSBaseConfigsClass


class GedisClientCmds:
    def __init__(self, client):
        self._client = client
        self.__dict__.update(client.cmds.__dict__)

    def __str__(self):
        output = "Gedis Client: (instance=%s) (address=%s:%-4s)" % (
            self._client.name,
            self._client.host,
            self._client.port,
        )
        if self._client.data.ssl:
            # FIXME: we should probably NOT print the key. this is VERY private information
            output += "\n(ssl=True, certificate:%s)" % self._client.sslkey
        return output

    __repr__ = __str__


class GedisClientFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.clients.gedis"
    _CHILDCLASS = GedisClient
