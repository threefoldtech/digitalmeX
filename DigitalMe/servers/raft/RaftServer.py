

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

import time

JSBASE = j.application.JSBaseClass

from pysyncobj.batteries import ReplDict
from pysyncobj import SyncObjConf


class RaftServer(JSBASE):
    def __init__(self, port, members, secret=""):
        JSBASE.__init__(self)

        self._members = members
        self.port = port
        self.dict1 = ReplDict()

        remotes = ["%s:%s" % item for item in self.members]

        cfg = SyncObjConf(autoTick=True)
        cfg.onReady = self.onReady
        if secret is not "" and secret is not None:
            print("SECRET")
            cfg.password = secret

        cfg.appendEntriesPeriod = 0.01
        cfg.appendEntriesUseBatch = True
        cfg.raftMinTimeout = 0.4
        cfg.raftMaxTimeout = 1.4
        cfg.dynamicMembershipChange = True
        cfg.onStateChanged = None
        cfg.commandsWaitLeader = False
        cfg.connectionRetryTime = 5.0  # connect to other down nodes every so many secs
        cfg.connectionTimeout = 3.5
        cfg.leaderFallbackTimeout = 10.0
        cfg.journalFile = "/tmp/raft/raft_%s" % self.port
        cfg.leaderFallbackTimeout = True
        cfg.logCompactionMinEntries = 1000
        cfg.logCompactionMinTime = 60

        self._log_debug("port:%s" % self.port)
        self._log_debug("members:%s" % remotes)
        # self._log_debug("secret:%s"%secret)

        self.syncobj = SyncObj("localhost:%s" % port, remotes, consumers=[self.dict1], conf=cfg)

        # for i in range(100000000):
        #     time.sleep(0.001)
        #     # self.syncobj.doTick()
        #     from IPython import embed;embed(colors='Linux')
        #     s

        while self.syncobj.isReady() == False:
            time.sleep(1)
            print("wait sync")
        time.sleep(1)
        self.start()

    def onReady(self):
        self._log_debug("READY")
        print(self.dict1.items())
        # self.start()

    @property
    def members(self):
        res = []
        for item in self._members.split(","):
            addr, port = item.split(":")
            addr = addr.strip()
            port = int(port)
            res.append((addr, port))
        return res

    def start(self):
        c = self.dict1.get("test:%s" % self.port)
        if c == None:
            self._log_debug("initial value for:%s" % self.port)
            self.dict1.set("test:%s" % self.port, 0, sync=True)
            self._log_debug("initial value DONE:%s" % self.port)

        speed = 0.1

        previnsert = 0.0
        prevprint = 0.0

        for i in range(100000000):
            time.sleep(0.001)
            last = time.time()

            if last > previnsert + 0.001:
                # print("insert")
                c = self.dict1.get("test:%s" % self.port)
                c = c + 1
                res = False
                while res == False:
                    try:
                        self.dict1.set("test:%s" % self.port, c, sync=True, timeout=5)
                        res = True
                    except Exception as e:
                        print("error in set:%s" % e.errorCode)
                        print(e)
                        time.sleep(0.1)

                previnsert = last

            if last > prevprint + 2.0:
                print(self.dict1.items())

                prevprint = last
