

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


class Farmer(j.application.JSBaseConfigClass):
    """
    one farmer instance
    """

    _SCHEMATEXT = """
        @url = threefold.grid.farmer
        name* = ""
        description = ""
        error = ""
        iyo_org* = ""
        wallets = (LS)
        emailaddr = (LS)
        mobile = (LS)
        """

    def _init(self, **kwargs):
        pass


class Farmers(j.application.JSBaseConfigsClass):
    """
    ...
    """

    _CHILDCLASS = Farmer
