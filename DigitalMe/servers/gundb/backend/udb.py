

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


import dbm
import json
import os


def format_object_id(schema, id):
    return "{}://{}".format(schema, id)


class UDB:
    def __init__(self, path="/tmp/gun.db"):
        if os.path.exists(path):
            self.db = dbm.open(path)
        else:
            self.db = dbm.open(path, "c")

    def get_object_by_id(self, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        try:
            return json.loads(self.db[full_id])
        except:
            return {"id": obj_id}

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        full_id = format_object_id(schema, obj_id)
        self.db[full_id] = json.dumps(obj)
        self.savedb()

    def savedb(self):
        self.db.close()

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
