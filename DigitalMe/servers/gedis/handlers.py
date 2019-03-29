from Jumpscale import j
from redis.exceptions import ConnectionError

from .protocol import RedisCommandParser, RedisResponseWriter

JSBASE = j.application.JSBaseClass

class Session():
    def __init__(self):
        self.dmid = None # is the digital me id e.g. kristof.ibiza
        self.admin = False

class Handler(JSBASE):
    def __init__(self, gedis_server):
        JSBASE.__init__(self)
        self.gedis_server = gedis_server
        self.cmds = {}  # caching of commands
        self.actors = self.gedis_server.actors
        self.cmds_meta = self.gedis_server.cmds_meta


    def handle_redis(self, socket, address):

        ##BUG: if we start a server with kosmos --debug it should get in the debugger but it does not if errors trigger, maybe something in redis?
        # w=self.t
        # raise RuntimeError("d")


        parser = RedisCommandParser(socket)
        response = RedisResponseWriter(socket)

        try:
            self._handle_redis_session(socket, address, parser, response)
        except ConnectionError as err:
            self._log_info('connection error: %s'% str(err),context="%s:%s"%address)
            print("connection error")
        finally:
            parser.on_disconnect()
            self._log_info('connection closed',context="%s:%s"%address)

    def _handle_redis_session(self, socket, address, parser, response):
        """
        deal with 1 specific session
        :param socket:
        :param address:
        :param parser:
        :param response:
        :return:
        """

        self._log_info("new incoming connection",context="%s:%s"%address)
        session = Session()

        while True:

            request = parser.read_request()

            #can have 2 or 3 parts, if 3 then the 3e one is the header

            if not request:  # empty list request
                # self.response.error('Empty request body .. probably this is a (TCP port) checking query')
                self._log_warning('wrong formatted request',context="%s:%s"%address)
                return

            #FOR DEBUG PURPOSES
            r = self._handle_request(session, request,address)
            response.encode(r)
            continue

            try:
                r = self._handle_request(session, request,address)
                response.encode(r)
            except Exception as e:
                # j.errorhandler.try_except_error_process(e, die=False)
                j.shell()
                w
                self._log_error(msg,context="%s:%s"%address)
                redis_cmd = request[0].decode("utf-8").lower()
                #now error in the handling of the request
                msg = "error: %s: %s"%(redis_cmd,str(e)).split("\n",1)[0]
                response.error(msg)



    def _handle_request(self,session, request,address):
        """
        deal with 1 specific request
        :param request: 
        :return: 
        """

        redis_cmd = request[0].decode("utf-8").lower()

        #process the predefined commands
        if redis_cmd == "command":
            return "OK"

        elif redis_cmd == "ping":
            return "PONG"

        elif redis_cmd == "auth":
            dmid,epoch,signature = request[1].decode("utf-8").split(",")
            #epoch has been given by remote client and has been signed by private key of the client
            #this allows us to verify the client, so we can check that his dmid is really from who we think it is
            return "OK"

        #header is {'content_type':'json', 'response_type':'capnp'} or {} if no header
        header = self._read_header(request)
        #content types supported auto,capnp, msgpack,json
        content_type = header.get('content_type', 'auto').casefold()    #is format of input
        response_type = header.get('response_type', 'auto').casefold()  #is format of what will be returned

        namespace, actor, command = self._command_split(redis_cmd)
        self._log_debug("command received %s %s %s" % (namespace, actor, command),context="%s:%s"%address)

        #cmd is cmd metadata + cmd.method is what needs to be executed
        cmd = self._cmd_obj_get(cmd=command, namespace=namespace, actor=actor)
        params_list = []
        params_dict = {}
        if cmd.schema_in:
            params_dict = self._read_input_args_schema(content_type, request, cmd)
        else:
            if len(request) > 1:
                params_list = request[1:]

            #the params are binary values now, no conversion happened

        #at this stage the input is in params as a dict

        #makes sure we understand which schema to use to return result from method

        if cmd.schema_out:
            params_dict["schema_out"] = cmd.schema_out

        #now execute the method() of the cmd
        result = None

        print("params cmd", params_list,  params_dict)
        result = cmd.method(*params_list,**params_dict)
        if isinstance(result, list):
            result = [self._result_encode(cmd,response_type,r) for r in result]
        else:
            result = self._result_encode(cmd,response_type,result)

        return result

    def _read_input_args_schema(self,content_type, request, command):
        """
        get the arguments from an input which is a schema
        :param content_type:
        :param request:
        :param cmd:
        :return:
        """

        def capnp_decode(request,command,die=True):
            try:
                # Try capnp which is combination of msgpack of a list of id/capnpdata
                id, data = j.data.serializers.msgpack.loads(request[1])
                args = command.schema_in.get(capnpbin=data)
                if id:
                    args.id = id
                return args
            except Exception as e:
                if die:
                    raise ValueError("the content is not valid capnp while you provided content_type=capnp\n%s\n%s"%(e,request[1]))
                return None

        def json_decode(request,command,die=True):
            try:
                args = command.schema_in.get(data=j.data.serializers.json.loads(request[1]))
                return args
            except Exception as e:
                if die:
                    raise ValueError("the content is not valid json while you provided content_type=json\n%s\n%s"%(str,request[1]))
                return None


        if content_type == 'auto':
                args = capnp_decode(request=request,command=command,die=False)
                if args is None:
                    args = json_decode(request=request,command=command)
        elif content_type == 'json':
            args = json_decode(request=request,command=command)
        elif content_type == 'capnp':
            args = capnp_decode(request=request,command=command)
        else:
            raise ValueError("invalid content type was provided the valid types are ['json', 'capnp', 'auto']")

        method_arguments = command.cmdobj.args
        if 'schema_out' in method_arguments:
            raise RuntimeError("schema_out should not be in arguments of method")

        params = {}

        for key in command.schema_in.propertynames:
            params[key] = getattr(args, key)

        return params

    def _cmd_obj_get(self, namespace, actor, cmd):
        """
        arguments come from self._command_split()
        will do caching of the populated command
        :param namespace: 
        :param actor: 
        :param cmd: 
        :return: the cmd object, cmd.method is the method to be executed
        """

        key = "%s__%s" % (namespace, actor)
        key_cmd = "%s__%s" % (key, cmd)

        # caching so we don't have to eval every time
        if key_cmd in self.cmds:
            return self.cmds[key_cmd]

        self._log_debug('command cache miss:%s %s %s' % (namespace, actor, cmd))
        if namespace == "system" and key not in self.actors:
            # we will now check if the info is in default namespace
            key = "default__%s" % actor
        if namespace == "default" and key not in self.actors:
            # we will now check if the info is in system namespace
            key = "system__%s" % actor

        if key not in self.actors:
            raise j.exceptions.Input("Cannot find cmd with key:%s in actors" % key)

        if key not in self.cmds_meta:
            raise j.exceptions.Input("Cannot find cmd with key:%s in cmds_meta" % key)

        meta = self.cmds_meta[key]

        # check cmd exists in the metadata
        if cmd not in meta.cmds:
            raise j.exceptions.Input("Cannot find method with name:%s in namespace:%s" % (cmd, namespace))

        cmd_obj = meta.cmds[cmd]

        try:
            cl = self.actors[key]
            cmd_method = getattr(cl, cmd)
        except Exception as e:
            raise j.exceptions.Input("Could not execute code of method '%s' in namespace '%s'\n%s" % (key, namespace, e))

        cmd_obj.method = cmd_method
        self.cmds[key_cmd] = cmd_obj

        return self.cmds[key_cmd]

    def _command_split(self,cmd, actor="system", namespace="system"):
        """

        :param cmd: command is in form x.x.x split in parts
        :param actor: is the default actor
        :param namespace: is the default namespace
        :return: (namespace, actor, cmd)
        """
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

    def _read_header(self,request):
        # if len(request) < 2:
        #     raise ValueError("can not handle with request, not enough arguments")

        # If request length is > 2 we will expect a header
        if len(request) > 2:
            return j.data.serializers.json.loads(request[2])
        return {}

    def _result_encode(self,cmd, response_type, item):

        if cmd.schema_out is not None:
            if response_type == 'msgpack':
                return item._msgpack
            elif response_type == 'capnp' or response_type == 'auto':
                return item._data
            else:
                raise j.exceptions.Input("cannot find required encoding type for return")
        else:

            if isinstance(item,j.data.schema.DataObjBase):
                if response_type == "json":
                    return item_json
                else:
                    return item._data
            return item
