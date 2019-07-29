

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


import json
import asyncio
import websockets
from .utils import newuid, new_node, ham_mix
from Jumpscale import j

JSConfigBase = j.application.JSBaseClass


def format_put_request(soul, **kwargs):
    ch = {"#": newuid(), "put": {soul: new_node(soul, **kwargs)}}
    return ch


def format_get_request(soul):
    ch = {"#": newuid(), "get": {"#": soul}}
    return ch


class Memory:
    def __init__(self):
        self.db = {}

    def put(self, soul, key, value, state):
        # soul -> {field:{'state':state, 'val':val, rel: relation}}
        if soul not in self.db:
            self.db[soul] = {"_": {}}
        self.db[soul][key] = value
        self.db[soul]["_"][key] = state

    def get(self, soul, key=None):
        # print("SOUL: ", soul, " KEY : ", key)
        ret = {"#": soul, "_": {"#": soul, ">": {}}}
        res = None
        if soul in self.db:
            if key and isinstance(key, str):
                res = {**ret, **self.db.get(soul)}
                return res.get(key, {})
            else:
                res = {**ret, **self.db.get(soul)}
                return res

        return ret

    def __setitem__(self, k, v):
        self.db[k] = v

    def __getitem__(self, k):
        return self.db[k]

    def list(self):
        return self.db.items()


TEMPLATE = """
addr = ""
port = 8080
base_url = "" 
user = ""
password_ = ""
"""


class GunClient(JSConfigBase):
    def __init__(self, instance, data=None, parent=None, interactive=True):
        if data is None:
            data = {}
        JSConfigBase.__init__(
            self, instance=instance, data=data, parent=parent, template=TEMPLATE, interactive=interactive
        )
        self.ws = None
        self.backend = Memory()

    @property
    def wsendpoint(self):
        return "ws://{addr}:{port}/gun".format(addr=self.config.data["addr"], port=self.config.data["port"])

    async def put(self, soul, **kwargs):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_put_request(soul, **kwargs)
            ch_str = json.dumps(ch)
            await ws.send(ch_str)
            resp = await ws.recv()
            return resp

    async def get(self, soul, key=None):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_get_request(soul)
            ch_str = json.dumps(ch)
            await ws.send(ch_str)
            resp = await ws.recv()
            loaded = json.loads(resp)
            change = loaded["put"]
            soul = loaded["#"]
            diff = ham_mix(change, self.backend)

            resp = {"@": soul, "#": newuid(), "ok": True}

            for soul, node in diff.items():
                for k, v in node.items():
                    if k == "_":
                        continue
                    self.backend.put(soul, k, v, diff[soul]["_"][">"][k])
            res = self.backend.get(soul, key) or "nil"
            return res
