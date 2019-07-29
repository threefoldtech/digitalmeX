

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


import os

import pytest
from DigitalMe.servers.gedis.GedisCmds import GedisCmds  # method_source_process


@pytest.mark.skip(
    reason="broken since https://github.com/threefoldtech/digitalmeX/commit/fd77fcb72150b2780d85e27db5ae4b4edd6a8539#diff-3e7b20d71613dda89b05c99227f0abb4"
)
@pytest.mark.parametrize(
    "input,code,comments,schema_in,schema_out,args",
    [
        (
            """def foo(self):
        pass""",
            "pass\n",
            "",
            "",
            "",
            [],
        ),
        (
            """def foo(self, a, b):
        pass""",
            "pass\n",
            "",
            "",
            "",
            ["a", "b"],
        ),
        (
            """def foo(self, a, b):
        \"""
        this is a comment
        \"""
        pass""",
            "pass\n",
            "this is a comment\n",
            "",
            "",
            ["a", "b"],
        ),
        (
            """def foo(self, a, b):
        \"""
        this is a comment
        ```in
        a = (O) !jumpscale.example.wallet
        ```
        ```out
        b = (O) !jumpscale.example.wallet
        ```
        \"""
        pass""",
            "pass\n",
            "this is a comment\n",
            "a = (O) !jumpscale.example.wallet\n",
            "b = (O) !jumpscale.example.wallet\n",
            ["a", "b"],
        ),
    ],
)
def test_method_source_process(input, code, comments, schema_in, schema_out, args):
    assert (code, comments, schema_in, schema_out, args) == method_source_process(input)


def test_GedisCmds_init():
    path = os.path.join(os.path.dirname(__file__), "actors/simple.py")
    cmds = GedisCmds(server=FakeServer(), namespace="default", name="test", path=path, data=None)
    assert cmds.name == "test"
    assert cmds.namespace == "default"
    assert cmds.path == path
    actual_commands = sorted(["ping", "foo", "bar", "echo"])
    assert list(cmds.cmds.keys()) == actual_commands
    for cmd in actual_commands:
        assert cmds.cmd_exists(cmd)


class FakeServer:
    def __init__(self):
        self.actors = {}
