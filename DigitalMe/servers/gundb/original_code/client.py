

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
from .backends import *
from .consts import METADATA, SOUL, STATE


def format_put_request(soul, **kwargs):
    ch = {SOUL: newuid(), "put": {soul: new_node(soul, **kwargs)}}
    return ch


def format_get_request(soul):
    ch = {SOUL: newuid(), "get": {SOUL: soul}}
    return ch


class GunClient:
    def __init__(self, wsendpoint="ws://localhost:8000/gun"):
        self.wsendpoint = wsendpoint
        self.ws = None
        self.backend = DummyKV()

    async def put(self, soul, **kwargs):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_put_request(soul, **kwargs)
            ch_str = json.dumps(ch)
            # print("Change: {} ".format(ch))
            await ws.send(ch_str)
            resp = await ws.recv()
            # print("RESP: {} ".format(resp))
            return resp

    async def get(self, soul, key=None):
        async with websockets.connect(self.wsendpoint) as ws:
            ch = format_get_request(soul)
            ch_str = json.dumps(ch)
            # print("Change: {} ".format(ch))
            await ws.send(ch_str)
            resp = await ws.recv()
            loaded = json.loads(resp)
            # print("RESP: {} ".format(resp))
            change = loaded["put"]
            # print("CHANGE IS: ", change)
            soul = loaded[SOUL]
            diff = ham_mix(change, self.backend)

            resp = {"@": soul, SOUL: newuid(), "ok": True}
            # print("DIFF:", diff)

            for soul, node in diff.items():
                for k, v in node.items():
                    if k == METADATA:
                        continue
                    kstate = 0
                    try:
                        kstate = diff[soul][METADATA][STATE][k]
                    except KeyError:
                        pass
                    else:
                        print("KSTATE: ", kstate)
                    self.backend.put(soul, k, v, kstate)
            return self.backend.get(soul, key)
