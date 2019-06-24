import json
from Jumpscale import j


JSBASE = j.application.JSBaseClass


class chatbot(JSBASE):
    """
    """

    def __init__(self):
        JSBASE.__init__(self)
        self.chatbot = self.server_gedis.chatbot

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
        return json.dumps({"sessionid": self.server_gedis.chatbot.session_new(topic)})
