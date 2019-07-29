

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


from collections import defaultdict
from .backend import BackendMixin


class cuteobj:
    def __getattr__(self, attr):
        if attr in dir(self):
            return getattr(self, attr)
        else:
            setattr(self, attr, cuteobj())

    def __str__(self):
        return "cuteobj: {} ".format(str(self.__dict__))


class MemoryDB(BackendMixin):
    def __init__(self):
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.objs = defaultdict(lambda: cuteobj())

    def get_object_by_id(self, obj_id, schema=None):
        return self.objs.get(obj_id, {})

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        self.objs[obj_id] = obj

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
