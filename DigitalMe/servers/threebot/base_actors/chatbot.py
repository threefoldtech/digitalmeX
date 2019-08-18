import json
from Jumpscale import j


class chatbot(j.application.ThreeBotActorBase):
    """
    """

    def _init(self, **kwargs):
        self.chatbot = self._gedis_server.chatbot

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
