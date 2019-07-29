

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


class CoordinatorBase(j.application.JSFactoryConfigsBaseClass):
    def __init__(self):
        j.application.JSFactoryConfigsBaseClass.__init__(self)
        self.services = {}
        self._name = self.__jslocation__.replace("j.world.", "")

    # def _service_action_ask(self,instance,name):
    #     cmd = [name,arg]
    #     self.q_in.put(cmd)
    #     rc,res = self.q_out.get()
    #     return rc,res

    # @property
    # def name(self):
    #     return self.data.name
    #
    # @property
    # def key(self):
    #     if self._key == None:
    #         self._key = "%s"%(j.core.text.strip_to_ascii_dense(self.name))
    #     return self._key

    def __str__(self):
        return "coordinator:%s" % self._name
