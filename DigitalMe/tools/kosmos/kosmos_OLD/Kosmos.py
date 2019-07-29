

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


class Kosmos(j.application.JSBaseClass):

    __jslocation__ = "j.tools.kosmos"

    def _init(self, **kwargs):
        pass

    def register_service(self, obj):
        raise RuntimeError()
        j.shell()

    def register_factory(self, location_source, location_dest):
        raise RuntimeError()
        j.shell()

    def __getattr__(self, attr):
        # if self.__class__._MODEL is None:
        #     return self.__getattribute__(attr)
        if attr in self.__class__._MODEL.schema.properties_list:
            return self.data.__getattribute__(attr)
        return self.__getattribute__(attr)
        # raise RuntimeError("could not find attribute:%s"%attr)

    def __dir__(self):
        r = self.__class__._MODEL.schema.properties_list
        for item in self.__dict__.keys():
            if item not in r:
                r.append(item)
        return r

    def __setattr__(self, key, value):
        if "data" in self.__dict__ and key in self.__class__._MODEL.schema.properties_list:
            # if value != self.data.__getattribute__(key):
            self._log_debug("SET:%s:%s" % (key, value))
            self.__dict__["data"].__setattr__(key, value)

        self.__dict__[key] = value

    def __str__(self):
        try:
            out = "%s\n%s\n" % (self.__class__.__name__, self.data)
        except:
            out = str(self.__class__) + "\n"
            out += j.core.text.prefix(" - ", self.data)
        return out

    __repr__ = __str__
