

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
from pickle import loads, dumps
import os


def format_object_id(schema, id):
    return "{}://{}".format(schema, id)


class Pickle(BackendMixin):
    def __init__(self, pickledbpath="/tmp/gundb.dat"):
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))
        self.pickledbpath = pickledbpath
        self.pickledb = None
        if os.path.exists(self.pickledbpath):
            with open(self.pickledbpath, "rb") as f:
                self.pickledb = loads(f.read())
        else:
            self.pickledb = {}

    def savedb(self):
        with open(self.pickledbpath, "wb") as f:
            f.write(dumps(self.pickledb))

    def get_object_by_id(self, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        return self.pickledb.get(full_id, {"id": obj_id})

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        self.pickledb[full_id] = obj
        self.savedb()

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
