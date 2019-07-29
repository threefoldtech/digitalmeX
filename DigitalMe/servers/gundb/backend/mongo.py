

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


class Mongo(BackendMixin):
    def __init__(self, connstring="mongodb://localhost:27017"):
        from pymongo import MongoClient

        self.cl = MongoClient(connstring)
        self.mongodb = self.cl.test_database
        self.db = defaultdict(lambda: defaultdict(lambda: defaultdict()))

    def get_object_by_id(self, obj_id, schema):
        col = self.mongodb[schema]
        obj = col.find_one({"id": obj_id})
        if not obj:
            col.insert_one({"id": obj_id})
            obj = col.find_one({"id": obj_id})
        return obj

    def set_object_attr(self, obj, attr, val):
        obj[attr] = val
        return obj

    def save_object(self, obj, obj_id, schema=None):
        col = self.mongodb[schema]
        col.find_one_and_update({"id": obj_id}, {"$set": obj}, upsert=True)

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()
