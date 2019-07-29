

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


TEMPLATE = """
members = "localhost:4441,localhost:4442,localhost:4443"
secret_ = ""
giturl = ""
cmd = ""
"""

JSConfigBase = j.application.JSBaseClass


class RaftCluster(JSConfigBase):
    def __init__(self, instance, data=None, parent=None, interactive=False):
        if data is None:
            data = {}
        JSConfigBase.__init__(
            self, instance=instance, data=data, parent=parent, template=TEMPLATE, ui=None, interactive=interactive
        )

    @property
    def members(self):
        res = []
        for item in self.config.data["members"].split(","):
            addr, port = item.split(":")
            addr = addr.strip()
            port = int(port)
            res.append((addr, port))
        return res

    def start(self, background=True):
        def sstart(port):
            members = ""
            for addr0, port0 in self.members:
                if int(port0) != int(port):
                    members += "%s:%s," % (addr0, port0)
            members = members.rstrip(",")

            cmd0 = self.config.data["cmd"]
            secret = self.config.data["secret_"]
            cmd = 'mkdir -p /tmp/raft;cd /tmp/raft;js_shell \'cl=%s;cl(port=%s,members="%s",secret="%s" )\'' % (
                cmd0,
                port,
                members,
                secret,
            )
            print(cmd)
            j.servers.tmux.execute(
                cmd, session="main", window="raft_%s" % port, pane="main", session_reset=False, window_reset=True
            )

        for addr, port in self.members:
            if addr in ["localhost", "127.0.0.1", "local"]:
                sstart(port)

        if not j.core.platformtype.myplatform.platform_is_osx:
            raise Exception(
                "issue #33 - implement to find local ipaddr and "
                "then based on own addr decide to start locally or not"
            )
            # from IPython import embed;embed(colors='Linux')
