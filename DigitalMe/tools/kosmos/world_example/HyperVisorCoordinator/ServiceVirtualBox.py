

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
import gevent

from DigitalMeLib.servers.digitalworld.BASE_CLASSES.ServiceBase import *


class ServiceVirtualBox(ServiceBase):

    _SCHEMA_TXT = """
    @url = world.hypervisor.virtualbox
    description = ""
    """

    # def __init__(self,id=None,name=None,servicepool=None):
    #     JSBASE.__init__(self,id,name,servicepool)

    @action
    def task1(self, descr):
        self._log_debug("TASK1:%s" % descr)
        return "RETURN:%s" % descr

    def task2(self, id):
        return "task2:%s" % id

    def monitor(self):
        print("monitor started")
        counter = 0
        while True:
            gevent.sleep(1)
            counter += 5
            print("monitor:%s:%s" % (self, counter))

    def ok(self):
        pass
