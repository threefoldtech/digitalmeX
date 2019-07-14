import json
from Jumpscale import j
from .backend.GunUtils import *
from .backend.MemoryDB import MemoryDB
from .backend.bcdb import BCDB
from geventwebsocket import WebSocketApplication
import uuid

# import os
# import sys
# import traceback
# import redis
# import time
# from time import sleep


class GeventGunServer(WebSocketApplication, j.application.JSBaseClass):
    def __init__(self, ws):
        WebSocketApplication.__init__(self, ws)
        j.application.JSBaseClass.__init__(self)

    def _init(self, **kwargs):
        self.db = BCDB()  # MemoryDB()
        self.graph = {}  # sometimes te MemoryDB is used sometimes the graph? whats difference
        self.peers = []
        self.trackedids = []

    def _trackid(self, id_):
        """
        :param id_:
        :return:
        """
        if id_ not in self.trackedids:
            self._log_debug("CREATING NEW ID:::", id_)
            self.trackedids.append(id_)
        return id_

    # def _emit(self, data):
    #     """
    #     is that being used? TODO:
    #     :param data:
    #     :return:
    #     """
    #     resp = json.dumps(data)
    #     for p in self.peers:
    #         self._log_debug("Sending resp: ", resp, " to ", p)
    #         p.send(resp)

    def _loggraph(self):
        pass
        # for soul, node in self.graph.items():
        #     self._log_debug("\nSoul: ", soul)
        #     self._log_debug("\n\t\tNode: ", node)
        #     for k, v in node.items():
        #         self._log_debug("\n\t\t{} => {}".format(k, v))

        # self._log_debug("TRACKED: ", self.trackedids, " #", len(self.trackedids))
        # self._log_debug("\n\nBACKEND: ", self.db.list())

    def on_open(self):
        self._log_debug("Got client connection")

    def on_message(self, message):
        resp = {"ok": True}
        if message is not None:
            msg = json.loads(message)
            if not isinstance(msg, list):
                msg = [msg]
            for payload in msg:
                if isinstance(payload, str):
                    payload = json.loads(payload)
                if "put" in payload:
                    change = payload["put"]
                    soul = payload["#"]
                    diff = ham_mix(change, self.graph)
                    uid = self._trackid(str(uuid.uuid4()))
                    self._loggraph()
                    resp = {"@": soul, "#": uid, "ok": True}
                    self._log_debug("DIFF:", diff)
                    for soul, node in diff.items():
                        for k, v in node.items():
                            if k == "_":
                                continue
                            val = json.dumps(v)
                            self.graph[soul][k] = val
                        for k, v in node.items():
                            if k == "_":
                                continue
                            val = json.dumps(v)
                            self.db.put(soul, k, v, diff[soul]["_"][">"][k], self.graph)

                elif "get" in payload:
                    get = payload["get"]
                    soul = get["#"]
                    ack = lex_from_graph(get, self.db)
                    uid = self._trackid(str(uuid.uuid4()))
                    self._loggraph()
                    resp = {"put": ack, "@": soul, "#": uid, "ok": True}

                self.sendall(resp)
                self.sendall(msg)

        self.ws.send(message)

    def on_close(self, reason):
        self._log_debug(reason)

    def sendall(self, resp):
        for client in self.ws.handler.server.clients.values():
            client.ws.send(json.dumps(resp))
