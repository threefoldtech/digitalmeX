

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
from gevent.pywsgi import WSGIServer

from radicale import application

JSConfigClient = j.application.JSBaseConfigClass


class RadicaleServer(JSConfigClient):
    _SCHEMATEXT = """
       @url =  jumpscale.servers.radicale
       name* = "default" (S)
       port = 11000 (I)
               """

    def install(self):
        """
        kosmos 'j.servers.gundb.install()'

        :return:
        """
        # j.builders.runtimes.python.pip_package_install("radicale")
        pass

    def start(self, name="radicale", background=False):
        """
        kosmos 'j.servers.webdav.start()'

        :param manual means the server is run manually using e.g. kosmos 'j.servers.rack.start(background=True)'

        """
        if not background:
            self.install()

            rack = j.servers.rack.get()
            server = WSGIServer(("0.0.0.0", self.port), application)
            rack.add(name=name, server=server)
            rack.start()

    def test(self):
        self.install(reset=reset)
        self.default.start()
        self.default.stop()
