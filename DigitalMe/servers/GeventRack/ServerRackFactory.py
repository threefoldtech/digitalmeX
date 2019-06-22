from Jumpscale import j

import gevent

from gevent import monkey

# from .Community import Community
from .ServerRack import ServerRack
from .Package import Package
import time
from gevent import event, sleep
import os
import socket
import netstr
import sys
import time

JSBASE = j.application.JSBaseClass


class ServerRackFactory(JSBASE):
    def __init__(self):
        self.__jslocation__ = "j.servers.rack"
        JSBASE.__init__(self)
        self.filemonitor = None
        # self.community = Community()
        self.packages = {}

    def start(self, secret, namespace="rack", restart=False, destroydata=False, zdbinternal=True):
        """
        kosmos 'j.servers.rack.start(secret="1234")'
        kosmos 'j.servers.rack.start(secret="1234",destroydata=True)'

        """

        if restart:
            j.shell()

        # make sure we have redis running
        j.clients.redis.core_get()

        if restart or not j.sal.nettools.tcpPortConnectionTest("localhost", 8081):
            j.servers.openresty.start()

        # #get sockexec to run
        if restart or not self._socket_check("/sandbox/var/exec.sock"):
            cmd = j.tools.tmux.cmd_get(
                name="runner", pane="p14", cmd="rm -f /sandbox/var/exec.sock;sockexec /sandbox/var/exec.sock"
            )
            cmd.stop()
            cmd.start()

        secret = j.data.hash.md5_string(
            secret
        )  # to make sure we don't have to store the secret as plain text somewhere

        self.nacl = j.data.nacl.get(
            name="rack", secret=j.data.hash.md5_string(secret + "rack")
        )  # just to make sure secret in nacl is not same as namespace

        if zdbinternal:
            j.servers.zdb.adminsecret = self.nacl.ssh_hash(secret + "admin")
            j.servers.zdb.name = "rack"

            if destroydata or restart:
                j.servers.zdb.stop()
                zdbrunning = False
            else:
                zdbrunning = j.servers.zdb.isrunning()

            if not zdbrunning:
                j.servers.zdb.start(destroydata=destroydata)

            try:
                cladmin = j.servers.zdb.client_admin_get()
            except Exception as e:
                if str(e).find("Access denied") != -1:
                    print(
                        "\nERROR:\n    cannot connect to ZDB, admin secret different, restart without ZDB init or destroy ZDB data\n"
                    )
                    sys.exit(1)
                raise e

            if not cladmin.namespace_exists(namespace):
                secretns = self.nacl.ssh_hash(
                    namespace + secret
                )  # will generate a unique hash which will only be relevant when right ssh-agent loaded
                zdbcl = cladmin.namespace_new(namespace, secret=secretns, maxsize=0, die=True)

        # self._run_exec("find /")
        # j.shell()
        # ws

        # def install_zrobot():
        #     path = j.clients.git.getContentPathFromURLorPath("https://github.com/threefoldtech/0-robot")
        #     j.sal.process.execute("cd %s;pip3 install -e ." % path)
        #
        # if "_zrobot" not in j.servers.__dict__.keys():
        #     # means not installed yet
        #     install_zrobot()

        env = {}
        env["addr"] = "localhost"
        env["port"] = "9900"
        env["namespace"] = namespace
        env["secret"] = secret
        cmd_ = "js_shell 'j.servers.rack.start_from_zdb()'"
        cmd = j.tools.tmux.cmd_get(name="rack", pane="p22", cmd=cmd_, env=env, process_strings=[])

        cmd.stop()
        cmd.start()

        gedisclient = j.clients.gedis.configure(
            namespace, namespace="system", port=8001, secret=secret, host="localhost"
        )

        assert gedisclient.system.ping() == b"PONG"

        return gedisclient

    def start_from_zdb(self, addr="localhost", port=9900, namespace="rack", secret="1234"):
        """

        examples:

        js_shell 'j.servers.rack.start_from_zdb()'

        :param addr: addr of starting zerodb namespace
        :param port: port
        :param namespace: name of the namespace
        :param secret: the secret of the namespace

        can also pass the arguments as env variables

        :return:




        """

        if "addr" in os.environ:
            addr = os.environ["addr"]
        if "port" in os.environ:
            port = int(os.environ["port"])
        if "namespace" in os.environ:
            namespace = os.environ["namespace"]
        if "secret" in os.environ:
            secret = os.environ["secret"]

        if len(secret) != 32:
            secret = j.data.hash.md5_string(secret)

        self.nacl = j.data.nacl.get(
            name="rack", secret=j.data.hash.md5_string(secret + "rack")
        )  # just to make sure secret in nacl is not same as namespace

        secretns = self.nacl.ssh_hash(
            namespace + secret
        )  # will generate a unique hash which will only be relevant when right ssh-agent loaded

        self.zdbclient = j.clients.zdb.client_get(nsname=namespace, addr=addr, port=port, secret=secretns, mode="seq")

        self.rack = self.server_rack_get()

        geventserver = j.servers.gedis.configure(
            host="localhost", port="8001", ssl=False, adminsecret=secret, instance=namespace
        )

        self.rack.add("gedis", geventserver.redis_server)  # important to do like this, otherwise 2 servers started

        key = "%s_%s_%s" % (addr, port, namespace)
        self.bcdb = j.data.bcdb.get("rack_%s" % key, zdbclient=self.zdbclient, cache=True)

        self.web_reload()

        self.rack.start()

    def server_rack_get(self):

        """
        returns a server rack

        to start the server manually do:
        js_shell 'j.servers.rack.start(namespace="test", secret="1234")'

        """

        return ServerRack()

    def test(self, manual=False):
        """
        js_shell 'j.servers.rack.test()'
        js_shell 'j.servers.rack.test(manual=True)'

        :param manual means the server is run manually using e.g. js_shell 'j.servers.rack.start()'

        """
        admincl = j.servers.zdb.start_test_instance(destroydata=True)
        cl = admincl.namespace_new("test", secret="1234")

        if manual:
            namespace = "system"
            # if server manually started can use this
            secret = "1234"
            gedisclient = j.clients.gedis.configure(
                namespace, namespace=namespace, port=8001, secret=secret, host="localhost"
            )
        else:
            # gclient will be gedis client
            gedisclient = self.start(addr=cl.addr, port=cl.port, namespace=cl.nsname, secret=cl.secret, background=True)

        # ns=gedisclient.core.namespaces()
        j.shell()
