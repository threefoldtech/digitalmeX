

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


import asyncio
from gundb.client import GunClient
from gundb.backends import *


async def test():
    import sys

    argv = sys.argv
    backend = DummyKV()
    if "dummy" in argv:
        backend = DummyKV()
    elif "memory" in argv:
        backend = Memory()
    elif "redis" in argv:
        backend = RedisKV()
    elif "udb" in argv:
        backend = UDB()
    elif "pickle" in argv:
        backend = Pickle()

    c = GunClient()
    c.backend = backend
    print(c.backend.db)
    await c.put("box", w=101, h=30)
    box = await c.get("box")
    print("Box is: ", box)
    w = await c.get("box", "w")
    print("W is : ", w)
    print(c.backend.db)


def cltest():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test())


if __name__ == "__main__":
    cltest()
