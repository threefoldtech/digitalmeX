

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

SCHEMA_IN = """
@url = gedis.test.in
foo = (S)
"""

SCHEMA_OUT = """
@url = gedis.test.out
bar = (S)
"""


class actor(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

    def ping(self):
        return "pong"

    def foo(self):
        return "foo"

    def bar(self):
        return "bar"

    def echo(self, input):
        return input

    def schema_in(self, x):
        """
        ```in
        x = (O) !gedis.test.in
        ```
        """
        return x.foo

    def schema_out(self, schema_out):
        """
        ```out
        !gedis.test.out
        ```
        """
        result = schema_out.new()
        result.bar = "test"
        return result

    def schema_in_out(self, x, schema_out):
        """
        ```in
        x = (O) !gedis.test.in
        ```

        ```out
        !gedis.test.out
        ```
        """
        result = schema_out.new()
        result.bar = x.foo
        return result

    def schema_in_list_out(self, x, schema_out):
        """
        ```in
        x = (O) !gedis.test.in
        ```

        ```out
        schema_out = (LO) !gedis.test.out
        ```
        """
        result = schema_out.new()
        result.bar = x.foo
        return [result, result]

    def args_in(self, foo, bar):
        """
        ```in
        foo = (S)
        bar = (I)
        ```
        """
        return "%s %s" % (foo, bar)

    def raise_error(self):
        raise RuntimeError("woopsy daisy")
