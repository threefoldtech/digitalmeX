

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
from Jumpscale import j


JSBASE = j.application.JSBaseClass


class chatbot(JSBASE):
    """
    """

    def _init(self, **kwargs):
        server = j.servers.gedis.get(self._parent_name_get().split("_")[1])
        self.chatbot = server.chatbot

        # check self.chatbot.chatflows for the existing chatflows
        # all required commands are here

    def work_get(self, sessionid):
        """
        ```in
        sessionid = "" (S)
        ```
        """
        res = self.chatbot.session_work_get(sessionid)
        return json.dumps(res)

    def work_report(self, sessionid, result):
        """
        ```in
        sessionid = "" (S)
        result = "" (S)
        ```
        """
        self.chatbot.session_work_set(sessionid, result)
        return

    def session_alive(self, sessionid, schema_out):
        # TODO:*1 check if greenlet is alive
        pass

    def ping(self):
        return "PONG"

    def session_new(self, topic):
        """
        ```in
        topic = "" (S)
        ```
        """
        return json.dumps(self.chatbot.session_new(topic))
