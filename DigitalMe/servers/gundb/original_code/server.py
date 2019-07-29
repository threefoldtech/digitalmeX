

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


from flask import Flask, request, send_from_directory, send_file, render_template, jsonify
from flask_sockets import Sockets
from time import sleep
import json
import os
from .utils import *
from .backends import *
import redis
import time
import uuid
import sys
import traceback


dir_path = os.path.dirname(os.path.realpath(__file__))


app = Flask(__name__)
app.backend = DummyKV()  # Pickle()
sockets = Sockets(app)


print("APP: ", app)


@app.route("/static/<path:path>")
def send_public(path):
    return send_from_directory("static" + "/" + path)


peers = []
graph = {}
trackedids = []


def trackid(id_):
    if id_ not in trackedids:
        print("CREATING NEW ID:::", id_)
        trackedids.append(id_)
    return id_


def emit(data):
    resp = json.dumps(data)
    for p in peers:
        print("Sending resp: ", resp, " to ", p)
        p.send(resp)


def loggraph(graph):
    global app
    for soul, node in graph.items():
        print("\nSoul: ", soul)
        print("\n\t\tNode: ", node)
        for k, v in node.items():
            print("\n\t\t{} => {}".format(k, v))

    print("TRACKED: ", trackedids, " #", len(trackedids))
    print("\n\nBACKEND: ", app.backend.list())


@sockets.route("/gun")
def gun(ws):

    global peers, graph
    # print("Got connection: ", ws)
    peers.append(ws)
    try:
        while not ws.closed:
            msgstr = ws.receive()
            # print("MSG :", msgstr)
            resp = {"ok": True}
            if msgstr is not None:
                msg = json.loads(msgstr)
                if not isinstance(msg, list):
                    msg = [msg]
                for payload in msg:
                    if isinstance(payload, str):
                        payload = json.loads(payload)
                    if "put" in payload:
                        change = payload["put"]
                        soul = payload["#"]
                        diff = ham_mix(change, graph)
                        uid = trackid(str(uuid.uuid4()))
                        loggraph(graph)
                        resp = {"@": soul, "#": uid, "ok": True}
                        print("DIFF:", diff)
                        for soul, node in diff.items():
                            for k, v in node.items():
                                if k == "_":
                                    continue
                                val = json.dumps(v)
                                app.backend.put(soul, k, v, diff[soul]["_"][">"][k])

                    elif "get" in payload:
                        get = payload["get"]
                        soul = get["#"]
                        ack = lex_from_graph(get, app.backend)
                        uid = trackid(str(uuid.uuid4()))
                        loggraph(graph)
                        resp = {"put": ack, "@": soul, "#": uid, "ok": True}

                emit(resp)
                emit(msg)
    except Exception as e:
        print("ERR:", e)
        traceback.print_exc(file=sys.stdout)
    # print("Connection closed for ws: ", ws)
    peers.remove(ws)
    print("Peers now are: ", peers)
