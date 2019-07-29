

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


from pprint import pprint as print

from Jumpscale import j

from .RaftServer import RaftServer
from .RaftCluster import RaftCluster


JSConfigBase = j.application.JSFactoryConfigsBaseClass


class RaftServerFactory(JSConfigBase):
    def __init__(self):
        self.__jslocation__ = "j.servers.raftserver"
        super(RaftServerFactory, self).__init__(RaftCluster)

    def get_by_params(
        self,
        instance="main",
        secret="1233",
        members="localhost:4441,localhost:4442,localhost:4443",
        cmd="j.servers.raftserver.example_server_class_get()",
    ):
        # TODO: use new style config management
        data = {}
        data["secret_"] = secret
        data["members"] = members
        data["cmd"] = cmd
        return self.get(instance=instance, data=data, create=True)

    def example_server_class_get(self):
        return RaftServer

    def start_local(
        self, nrservers=3, startport=4000, cmd="j.servers.raftserver.example_server_class_get()", secret="1233"
    ):
        """
        start local cluster of 5 nodes, will be run in tmux
        """
        members = ""
        for i in range(nrservers):
            members += "localhost:%s," % (startport + i)

        members = members.rstrip(",")

        cluster = self.get_by_params(instance="main", secret=secret, members=members, cmd=cmd)
        cluster.start(background=True)

    def test(self):
        """
        js_shell 'j.servers.raftserver.test()'
        """
        self.start_local(nrservers=4, startport=6000, cmd="j.servers.raftserver.example_server_class_get()")

    def test_nopasswd(self):
        """
        js_shell 'j.servers.raftserver.test_nopasswd()'
        """
        self.start_local(nrservers=4, startport=6000, cmd="j.servers.raftserver.example_server_class_get()", secret="")
