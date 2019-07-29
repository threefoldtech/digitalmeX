

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
from .OpenPublish import OpenPublish

JSConfigs = j.application.JSBaseConfigsClass
from .ThreebotServer import ThreeBotServer


class ThreeBotServersFactory(j.application.JSBaseConfigsClass):
    """
    Factory for 3bots
    """

    __jslocation__ = "j.servers.threebot"
    _CHILDCLASS = ThreeBotServer

    def _init(self):
        self._default = None

    @property
    def default(self):
        if not self._default:
            self._default = self.get("default")
        return self._default

    def bcdb_get(self, name, secret="", use_zdb=False):
        return self.default.bcdb_get(name, secret, use_zdb)

    def test(self):
        """

        kosmos 'j.servers.threebot.test()'

        :return:
        """

        s = self.default
        s.start()

        j.shell()
