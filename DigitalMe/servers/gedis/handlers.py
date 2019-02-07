from Jumpscale import j
from redis.exceptions import ConnectionError

from .protocol import RedisCommandParser, RedisResponseWriter

JSBASE = j.application.JSBaseClass


class Handler(JSBASE):
    def __init__(self, gedis_server):
        JSBASE.__init__(self)
        self.gedis_server = gedis_server
        self.cmds = {}  # caching of commands
        self.classes = self.gedis_server.classes
        self.cmds_meta = self.gedis_server.cmds_meta


    def handle_redis(self, socket, address):
        parser = RedisCommandParser(socket)
        response = RedisResponseWriter(socket)

        try:
            self._handle_redis(socket, address, parser, response)
        except ConnectionError as err:
            # self._log_info('connection error', error=str(err), address=address)
            print("connection error")
        finally:
            parser.on_disconnect()
            # self._log_info('connection closed', address=address)

    def _handle_redis(self, socket, address, parser, response):
        # log = self._log_bind(address=address)  # requires stuctlog, for future
        # log = self._logger
        # log.info('new incoming connection')

        socket.namespace = "system"

        while True:
            request = parser.read_request()

            if request is None:
                # log.debug("connection lost or tcp test")
                break

            if not request:  # empty list request
                # self.response.error('Empty request body .. probably this is a (TCP port) checking query')
                # log.debug("wrong formatted request")
                continue

            cmd = request[0]
            redis_cmd = cmd.decode("utf-8").lower()

            # special command to put the client on right namespace
            if redis_cmd == "select":
                # log.debug('start namespace selection')
                socket.namespace, found = select_namespace(request)
                if not found:
                    response.error("could not find namespace")
                # log.debug("namespace selected %s" % socket.namespace)
                response.encode('OK')
                continue

            if redis_cmd == "command":
                response.encode("OK")
                continue

            if redis_cmd == "ping":
                response.encode("PONG")
                continue

            if redis_cmd == "auth":
                response.encode("OK")
                continue

            namespace, actor, command = command_split(redis_cmd, namespace=socket.namespace)
            # log.debug("command received %s %s %s" % (namespace, actor, command))

            cmd, err = self.command_obj_get(cmd=command, namespace=namespace, actor=actor)
            if err:
                response.error(err)
                # log.error("fail to get command %s %s" % (namespace, command))
                continue

            header = {}
            params = {}
            if cmd.schema_in:
                try:
                    header = read_header(request)
                except ValueError:
                    response.error("Invalid header was provided, "
                                   "the header should be a json object with the key header, "
                                   "e.g: {'content_type':'json', 'response_type':'capnp'})")
                    continue

                try:
                    input_args = read_input_args(request, header, cmd)
                except ValueError as err:
                    response.error(str(err))
                    continue

                # FIXME: avoid using eval
                method_arguments = cmd.cmdobj.args
                if 'schema_out' in method_arguments:
                    method_arguments.remove('schema_out')


                for key in method_arguments:
                    if key.find('=') != -1:
                        # with default
                        key, default = key.split('=')
                        params[key] = getattr(input_args, key, default)
                    else:
                        params[key] = getattr(input_args, key)

            else:
                if len(request) > 1:
                    params = request[1:]

            if cmd.schema_out:
                params["schema_out"] = cmd.schema_out

            result = None
            try:
                print("parms cmd",params)
                if params == {}:
                    result = cmd.method()
                elif j.data.types.list.check(params):
                    result = cmd.method(*params)
                else:
                    result = cmd.method(**params)
            except Exception as e:
                # log.error("exception in redis server: %s" % str(e))
                j.errorhandler.try_except_error_process(e, die=False)
                msg = str(e)
                msg += "\nCODE:%s:%s\n" % (cmd.namespace, cmd.name)
                response.error(msg)
                continue

            def should_encode(item):
                response_type = header.get('response_type', 'auto')
                content_type = header.get('content_type', 'auto')
                if cmd.schema_out and hasattr(item, '_data'):
                    if response_type == 'capnp' or (response_type == 'auto' and (content_type in ['capnp', 'auto'])):
                        item = item._data
                return item

            if isinstance(result, list):
                result = [should_encode(r) for r in result]
            else:
                result = should_encode(result)

            response.encode(result)

    def command_obj_get(self, namespace, actor, cmd):

        key = "%s__%s" % (namespace, actor)
        key_cmd = "%s__%s" % (key, cmd)

        # caching so we don't have to eval every time
        if key_cmd in self.cmds:
            return self.cmds[key_cmd], ''

        # self._log_debug('command cache miss:%s %s %s' % (namespace, actor, cmd))
        if namespace == "system" and key not in self.classes:
            # we will now check if the info is in default namespace
            key = "default__%s" % actor
        if namespace == "default" and key not in self.classes:
            # we will now check if the info is in system namespace
            key = "system__%s" % actor

        if key not in self.classes:
            return None, "Cannot find cmd with key:%s in classes" % key

        if key not in self.cmds_meta:
            return None, "Cannot find cmd with key:%s in cmds_meta" % key

        meta = self.cmds_meta[key]

        # check cmd exists in the metadata
        if cmd not in meta.cmds:
            return None, "Cannot find method with name:%s in namespace:%s" % (cmd, namespace)

        cmd_obj = meta.cmds[cmd]

        try:
            cl = self.classes[key]
            cmd_method = getattr(cl, cmd)
        except Exception as e:
            return None, "Could not execute code of method '%s' in namespace '%s'\n%s" % (key, namespace, e)

        cmd_obj.method = cmd_method
        self.cmds[key_cmd] = cmd_obj

        return self.cmds[key_cmd], ""


def select_namespace(request):
    namespace = request[1].decode()

    try:
        i = int(namespace)
        # means is selection of DB in redis directly because is int
        return (namespace, True)
    except Exception:
        pass

    if namespace not in j.servers.gedis.latest.namespaces:
        return (namespace, False)

    return (namespace, True)


def command_split(cmd, actor="system", namespace="system"):
    cmd_parts = cmd.split(".")
    if len(cmd_parts) == 3:
        namespace = cmd_parts[0]
        actor = cmd_parts[1]
        if "__" in actor:
            actor = actor.split("__", 1)[1]
        cmd = cmd_parts[2]

    elif len(cmd_parts) == 2:
        actor = cmd_parts[0]
        if "__" in actor:
            actor = actor.split("__", 1)[1]
        cmd = cmd_parts[1]
        if actor == "system":
            namespace = "system"
    elif len(cmd_parts) == 1:
        namespace = "system"
        actor = "system"
        cmd = cmd_parts[0]
    else:
        raise RuntimeError("cmd not properly formatted")

    return namespace, actor, cmd


def read_header(request):
    if len(request) < 2:
        raise ValueError("can not handle with request, not enough arguments")

    # If request length is > 2 we will expect a header
    if len(request) > 2:
        return j.data.serializers.json.loads(request[2])
    return {}


def read_input_args(request, header, command):

    content_type = header.get('content_type', 'auto').casefold()

    if content_type == 'auto':
        try:
            # Try capnp
            id, data = j.data.serializers.msgpack.loads(request[1])
            args = command.schema_in.get(capnpbin=data)
            if id:
                args.id = id
            content_type = 'capnp'
        except Exception:
            # Try Json
            args = command.schema_in.get(data=j.data.serializers.json.loads(request[1]))
            content_type = 'json'

    elif content_type == 'json':
        try:
            args = command.schema_in.get(data=j.data.serializers.json.loads(request[1]))
        except Exception:
            raise ValueError("the content is not valid json while you provided content_type=json")
    elif content_type == 'capnp':
        try:
            id, data = j.data.serializers.msgpack.loads(request[1])
            args = command.schema_in.get(capnpbin=data)
            if id:
                args.id = id
        except Exception:
            raise ValueError("the content is not valid capnp while you provided content_type=capnp")
    else:
        raise ValueError("invalid content type was provided the valid types are ['json', 'capnp', 'auto']")

    return args
    # def handle_websocket(self,socket, namespace):
    #
    #     message = socket.receive()
    #     if not message:
    #         return
    #     message = json.loads(message)
    #     namespace,actor,cmd = self.command_split(message["command"],namespace=namespace)
    #     cmd, err = self.command_obj_get(namespace,actor,cmd)
    #     if err:
    #         socket.send(err)
    #         return
    #
    #     res, err = self.handle_websocket_(cmd, message,namespace=namespace)
    #     if err:
    #         socket.send(err)
    #         return
    #
    #     socket.send(json.dumps(res))
    #
    # def handle_websocket_(self, cmd, message,namespace):
    #
    #     if cmd.schema_in:
    #         if not message.get("args"):
    #             return None, "need to have arguments, none given"
    #
    #         o = cmd.schema_in.get(data=j.data.serializers.json.loads(message["args"]))
    #         args = [a.strip() for a in cmd.cmdobj.args.split(',')]
    #         if 'schema_out' in args:
    #             args.remove('schema_out')
    #         params = {}
    #         schema_dict = o._ddict
    #         if len(args) == 1:
    #             if args[0] in schema_dict:
    #                 params.update(schema_dict)
    #             else:
    #                 params[args[0]] = o
    #         else:
    #             params.update(schema_dict)
    #
    #         if cmd.schema_out:
    #             params["schema_out"] = cmd.schema_out
    #     else:
    #         if message.get("args"):
    #             params = message["args"]
    #             if cmd.schema_out:
    #                 params.append(cmd.schema_out)
    #         else:
    #             params = None
    #
    #     try:
    #         if params is None:
    #             result = cmd.method()
    #         elif j.data.types.list.check(params):
    #             result = cmd.method(*params)
    #         else:
    #             result = cmd.method(**params)
    #         return result, None
    #
    #     except Exception as e:
    #         self._log_debug("exception in redis server")
    #         eco = j.errorhandler.parsePythonExceptionObject(e)
    #         msg = str(eco)
    #         msg += "\nCODE:%s:%s\n" % (cmd.namespace, cmd.name)
    #         self._log_debug(msg)
    #         return None, e.args[0]
