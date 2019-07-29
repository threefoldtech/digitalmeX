

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

JSBASE = j.application.JSBaseClass

SCHEMA = """
{{obj.text}}
"""


class model(JSBASE):

    def __init__(self, client):
        JSBASE.__init__(self)
        self.name = "{{obj.name}}"
        self.url = "{{obj.url}}"
        self.schema = j.data.schema.get_from_url_latest(url=self.url)
        self.client = client
        self.redis = client.redis

    def set(self, obj):
        bdata = j.data.serializers.msgpack.dumps([obj.id, obj.data])
        res = self.redis.execute_command("model_%s.set" % self.name, bdata)
        id, _ = j.data.serializers.msgpack.loads(res)
        obj.id = id
        return obj

    def get(self, id):
        res = self.redis.execute_command("model_%s.get" % self.name, str(id))
        id, data = j.data.serializers.msgpack.loads(res)
        obj = self.schema.new(data=data)
        obj.id = id
        return obj

    def find(self, total_items_in_page=20, page_number=1, only_fields=[], {{find_args}}):
        items = self.redis.execute_command("model_%s.find" %
                                           self.name, total_items_in_page, page_number, only_fields, {{kwargs}})
        items = j.data.serializers.msgpack.loads(items)
        result = []

        for item in items:
            id, data = j.data.serializers.msgpack.loads(item)
            obj = self.schema.new(data=data)
            obj.id = id
            result.append(obj)
        return result

    def new(self):
        return self.schema.new()

    def __str__(self):
        return "MODEL%s" % self.url

    __repr__ = __str__
