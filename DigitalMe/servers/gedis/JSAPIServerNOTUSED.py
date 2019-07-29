

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


from .handlers import WebsocketRequestHandler
from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi

# THINK IS NOT USED AT THIS POINT


class JSAPIServer:
    def __init__(self):
        self.websocket_server = pywsgi.WSGIServer(("0.0.0.0", 8001), self.websocketapp, handler_class=WebSocketHandler)

    def websocketapp(self, environ, start_response):
        if "/static/" in environ["PATH_INFO"]:
            # items = [p for p in environ['PATH_INFO'].split('/static/') if p]
            # if len(items) == 1:
            #     static_file = items[-1]
            #     if static_file in self.static_files:
            #         start_response('200 OK', [('Content-Type', 'application/javascript;charset=utf-8'),('Access-Control-Allow-Origin','*')])
            #         return [self.code_js_client]

            # file_path = j.sal.fs.joinPaths(self.static_files_path, static_file)
            # if j.sal.fs.exists(file_path):
            #     self.static_files[static_file] = j.sal.fs.readFile(file_path).replace('%%host%%', host).encode('utf-8')
            start_response(
                "200 OK",
                [("Content-Type", "application/javascript;charset=utf-8"), ("Access-Control-Allow-Origin", "*")],
            )
            code_js = self.code_js_client
            host = environ.get("HTTP_HOST")
            #
            code_js = code_js.replace("wss://", "ws://")
            code_js = code_js.replace("%%host%%", host).encode("utf-8")
            return [code_js]

            # start_response('404 NOT FOUND', [])
            # return []

        websocket = environ.get("wsgi.websocket")
        if not websocket:
            return []
        addr = "{0}:{1}".format(environ["REMOTE_ADDR"], environ["REMOTE_PORT"])
        handler = WebsocketRequestHandler(self.instance, self.cmds, self.actors, self.cmds_meta)
        handler.handle(websocket, addr)
        return []
