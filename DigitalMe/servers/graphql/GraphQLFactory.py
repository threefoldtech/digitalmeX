from Jumpscale import j

JSBASE = j.application.JSBaseClass

from bottle import route, template, request, Bottle, abort, template, static_file

class GraphQLFactory(JSBASE):

    __jslocation__ = "j.servers.graphql"

    def _init(self):
        self._logger_enable()


    def install(self):
        """
        kosmos 'j.servers.gundb.install()'

        :return:
        """
        j.builders.runtimes.python.pip_package_install("bottle")
        j.builders.runtimes.python.pip_package_install("graphene >= 2.0.dev20170802065539")
        j.builders.runtimes.python.pip_package_install("flake8")
        j.builders.runtimes.python.pip_package_install("tox")

    def _server_test_start(self, background=False):
        """
        kosmos 'j.servers.graphql._server_test_start()'

        :param manual means the server is run manually using e.g. kosmos 'j.servers.rack.start(background=True)'

        """

        if not background:

            self.install()

            rack = j.servers.rack.get()

            from bottle import request, Bottle, abort, static_file, template
            from .GraphqlBottle import graphql_middleware
            from geventwebsocket import WebSocketError
            from .schema import schema



            app = Bottle()

            # expose graphql end point
            graphql_middleware(app, '/graphql', schema)

            # expose graphiql
            @app.route("/graphiql")
            def graphiql():
                return static_file("graphiql.html", root="%s/html" % self._dirpath)

            # expose test websockets app
            @app.route("/websocket")
            def websockets():
                return template("""
                <!DOCTYPE html>
                <html>
                <head>
                  <script type="text/javascript">
                    var ws = new WebSocket("ws://172.17.0.2:7778/websockets");
                    ws.onopen = function() {
                        ws.send("Hello, world");
                    };
                    ws.onmessage = function (evt) {
                        alert(evt.data);
                    };
                  </script>
                </head>
                </html>
                """)


            # websockets app
            websockets_app = Bottle()

            @websockets_app.route('/websockets')
            def handle_websocket():
                wsock = request.environ.get('wsgi.websocket')
                if not wsock:
                    abort(400, 'Expected WebSocket request.')

                while True:
                    try:
                        message = wsock.receive()
                        wsock.send("Your message was: %r" % message)
                    except WebSocketError:
                        break



            # add a bottle webserver to it
            rack.bottle_server_add(name="graphql", port=7777, app=app)
            rack.bottle_server_add(name="graphql_subscriptions", port=7778, app=websockets_app, websocket=True)
            rack.start()

        else:

            S = """
            from gevent import monkey
            monkey.patch_all(subprocess=False)
            from Jumpscale import j
            
            #start the graphql server using gevent rack
            j.servers.graphql._server_test_start()
                        
            """

            S = j.core.tools.text_replace(S, args)

            s = j.servers.startupcmd.new(name="graphql_test")
            s.cmd_start = S
            # the MONKEY PATCH STATEMENT IS A WEIRD ONE, will make sure that before starting monkeypatching will be done
            s.executor = "tmux"
            s.interpreter = "python"
            s.timeout = 10
            s.ports = 7766
            if not s.is_running():
                s.stop()
            s.start()

    def test(self):
        """
        kosmos 'j.servers.gundb.test()'

        """

        self._server_test_start(background=True)
        

        print("tests are ok")
