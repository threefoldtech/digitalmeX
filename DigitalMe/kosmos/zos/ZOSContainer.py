

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


from Jumpscale import j


class ZOSContainer(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.clients.zoscmd.zoscontainer.1
    name* = "" (S)
    zos_node_instance = "" (S) #name to the instance of the ZOSNode
    ssh_client_instance = "" (S) #name of the ssh client instance (if already created), namne will be zos_container_$name
    flist = ""
    env = "" #k
    ports = "" (dict)
    
    
    """

    def _init(self, ZOSNode):
        self.ZOSNode = None  # links to the ZOSNode which hosts this ZOSContainer

        # TODO: need to add relevant info in schema above
        # self.name = name
        # self.node = node
        # self.mounts = mounts or {}
        # self.hostname = hostname
        # self.flist = flist
        # self.ports = ports or {}
        # self._nics = nics or []
        # self.host_network = host_network
        # self.storage = storage
        # self.init_processes = init_processes or []
        # self.privileged = privileged
        # self._identity = identity
        # self.env = env or {}
        # self._client = None
        # self.logger = logger or default_logger
        #
        # for nic in self.nics:
        #     nic.pop('ztClient', None)
        #     if nic.get('config', {}).get('gateway', ''):
        #         nic['monitor'] = True

        # TODO: need to go over all methods & make compatible with our config mgmt

    @classmethod
    def from_containerinfo(cls, containerinfo, node, logger=None):
        logger = logger or default_logger
        self._log_debug("create container from info")

        arguments = containerinfo["container"]["arguments"]
        return cls(
            name=arguments["name"],
            node=node,
            flist=arguments["root"],
            hostname=arguments["hostname"],
            mounts=arguments["mount"],
            nics=arguments["nics"],
            host_network=arguments["host_network"],
            ports=arguments["port"],
            storage=arguments["storage"],
            privileged=arguments["privileged"],
            identity=arguments["identity"],
            env=arguments["env"],
            logger=logger,
        )

    @property
    def zos_client(self):
        """
        return zos protocol client
        :return:
        """
        pass

    @property
    def ssh_client(self):
        """

        :return: ssh client to this container
        """
        pass
        # implement caching at client side

    def start(self):
        if not self.is_running():
            self._log_debug("start %s", self)
            self._create_container()
            for process in self.init_processes:
                cmd = "{} {}".format(process["name"], " ".join(process.get("args", [])))
                pwd = process.get("pwd", "")
                stdin = process.get("stdin", "")
                id = process.get("id")
                env = {}
                for x in process.get("environment", []):
                    k, v = x.split("=")
                    env[k] = v
                self.client.system(command=cmd, dir=pwd, stdin=stdin, env=env, id=id)

        assert self.running() == True

    def stop(self):
        """
        will stop the container and also his mountpoints
        :return:
        """
        if not self.is_running():
            return
        self._log_debug("stop %s", self)

        self.node.client.container.terminate(self.id)
        self._client = None

    def is_running(self):
        return self.node.is_running() and self.id is not None

    #

    def test(self):
        pass
        # do a basic test, look for client (e.g. start an ubuntu 18.04 container)
        # make connection
        # some test

    @property
    def id(self):
        self._log_debug("get container id")
        info = self.info
        if info:
            return info["container"]["id"]
        return

    @property
    def info(self):
        self._log_debug("get container info")
        for containerid, container in self.node.client.container.list().items():
            if self.name == container["container"]["arguments"]["name"]:
                containerid = int(containerid)
                container["container"]["arguments"]["identity"] = self._identity
                if self._client and self._client.container != containerid:
                    self._client = None
                container["container"]["id"] = int(containerid)
                return container
        return

    @property
    def identity(self):
        if not self._identity:
            if self.is_running():
                for nic in self.nics:
                    if nic["type"] == "zerotier":
                        self._identity = self.client.zerotier.info()["secretIdentity"]
        return self._identity

    @property
    def public_identity(self):
        if self.is_running():
            for nic in self.nics:
                if nic["type"] == "zerotier":
                    return self.client.zerotier.info()["publicIdentity"]

    @property
    def ipv6(self, interface=None):
        """
        return a list of all the ipv6 present in the container

        the local ip are skipped

        :param interface: only return the ips of a certain interface.
                          If none scan all the existing interfaces , defaults to None
        :param interface: str, optional
        :return: list of ip
        :rtype: list
        """

        interfaces = [interface]
        if interface is None:
            interfaces = [l["name"] for l in self.client.ip.link.list() if l["name"] not in ["lo"]]

        ips = []
        for interface in interfaces:
            for ip in self.client.ip.addr.list(interface):
                network = netaddr.IPNetwork(ip)
                if network.version == 6 and network.is_link_local() is False:
                    ips.append(network.ip)
        return ips

    def default_ip(self, interface=None):
        """
        Returns the ip if the container has a default nic
        :return: netaddr.IPNetwork
        """
        if interface is None:
            for route in self.client.ip.route.list():
                if route["gw"]:
                    interface = route["dev"]
                    break
            else:
                raise LookupError("Could not find default interface")
        for ipaddress in self.client.ip.addr.list(interface):
            ip = netaddr.IPNetwork(ipaddress)
            if ip.version == 4:
                break
        else:
            raise LookupError("Failed to get default ip")
        return ip

    def add_nic(self, nic):
        self.node.client.container.nic_add(self.id, nic)

    def remove_nic(self, nicname):
        for idx, nic in enumerate(self.info["container"]["arguments"]["nics"]):
            if nic["state"] == "configured" and nic["name"] == nicname:
                break
        else:
            return
        self.node.client.container.nic_remove(self.id, idx)

    @property
    def client(self):
        if not self._client:
            self._client = self.node.client.container.client(self.id)
        return self._client

    def upload_content(self, remote, content):
        if isinstance(content, str):
            content = content.encode("utf8")
        bytes = BytesIO(content)
        self.client.filesystem.upload(remote, bytes)

    def download_content(self, remote):
        buff = BytesIO()
        self.client.filesystem.download(remote, buff)
        return buff.getvalue().decode()

    def _create_container(self, timeout=60):
        self._log_debug("send create container command to zero-os (%s)", self.flist)
        tags = [self.name]
        if self.hostname and self.hostname != self.name:
            tags.append(self.hostname)

        # Populate the correct mounts dict
        if type(self.mounts) == list:
            mounts = {}
            for mount in self.mounts:
                try:
                    sp = self.node.storagepools.get(mount["storagepool"])
                    fs = sp.get(mount["filesystem"])
                except KeyError:
                    continue
                mounts[fs.path] = mount["target"]
            self.mounts = mounts

        job = self.node.client.container.create(
            root_url=self.flist,
            mount=self.mounts,
            host_network=self.host_network,
            nics=self.nics,
            port=self.ports,
            tags=tags,
            name=self.name,
            hostname=self.hostname,
            storage=self.storage,
            privileged=self.privileged,
            identity=self.identity,
            env=self.env,
        )

        if self.is_running():
            self.identity

        self._client = self.node.client.container.client(int(job.get(timeout)))

    def is_job_running(self, id):
        try:
            for _ in self.client.job.list(id):
                return True
            return False
        except Exception as err:
            if str(err).find("invalid container id"):
                return False
            raise

    def stop_job(self, id, timeout=30):
        signal = signal.SIGTERM
        is_running = self.is_job_running(id)
        if not is_running:
            return

        self._log_debug("stop job: %s", id)

        self.client.job.kill(id)

        # wait for the daemon to stop
        start = time.time()
        end = start + timeout
        is_running = self.is_job_running(id)
        while is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_job_running(id)

        if is_running:
            raise RuntimeError("Failed to stop job {}".format(id))

    def is_port_listening(self, port, timeout=60, network=("tcp", "tcp6")):
        def is_listening():
            for lport in self.client.info.port():
                if lport["network"] in network and lport["port"] == port:
                    return True
            return False

        if timeout:
            start = time.time()
            while start + timeout > time.time():
                if is_listening():
                    return True
                time.sleep(1)
            return False
        else:
            return is_listening()

    @property
    def nics(self):
        if self.is_running():
            return list(filter(lambda nic: nic["state"] == "configured", self.info["container"]["arguments"]["nics"]))
        else:
            nics = []
            for nic in self._nics:
                nic.pop("state", None)
                nics.append(nic)

            return nics

    def waitOnJob(self, job):
        MAX_LOG = 15
        logs = []

        def callback(lvl, message, flag):
            if len(logs) == MAX_LOG:
                logs.pop(0)
            logs.append(message)

            if flag & 0x4 != 0:
                erroMessage = " ".join(logs)
                raise RuntimeError(erroMessage)

        resp = self.client.subscribe(job.id)
        resp.stream(callback)

    def get_forwarded_port(self, port):
        for k, v in self.ports.items():
            if v == port:
                return int(k.split(":")[-1])

    def authorize_networks(self, nics):
        public_identity = self.public_identity
        if not public_identity:
            raise RuntimeError("Failed to get zerotier public identity")
        for nic in nics:
            if nic["type"] == "zerotier":
                client = j.clients.zerotier.get(nic["ztClient"], create=False, die=True, interactive=False)
                network = client.network_get(nic["id"])
                network.member_add(public_identity, self.name)

    @property
    def mgmt_addr(self):
        return get_zt_ip(self.client.info.nic())

    def __str__(self):
        return j.core.tools.text_replace(
            "{RED}zoscontainer{RESET}:%-14s %-25s:%-4s" % (self.name, self.addr, self.port)
        )

    __repr__ = __str__

    # @property
    # def identity(self):
    #     if not self._identity:
    #         if self.is_running():
    #             for nic in self.nics:
    #                 if nic['type'] == 'zerotier':
    #                     self._identity = self.client.zerotier.info()['secretIdentity']
    #     return self._identity
    #
    # @property
    # def ipv6(self, interface=None):
    #     """
    #     return a list of all the ipv6 present in the container
    #
    #     the local ip are skipped
    #
    #     :param interface: only return the ips of a certain interface.
    #                       If none scan all the existing interfaces , defaults to None
    #     :param interface: str, optional
    #     :return: list of ip
    #     :rtype: list
    #     """
    #
    #     interfaces = [interface]
    #     if interface is None:
    #         interfaces = [l['name'] for l in self.client.ip.link.list() if l['name'] not in ['lo']]
    #
    #     ips = []
    #     for interface in interfaces:
    #         for ip in self.client.ip.addr.list(interface):
    #             network = netaddr.IPNetwork(ip)
    #             if network.version == 6 and network.is_link_local() is False:
    #                 ips.append(network.ip)
    #     return ips
    #
    # def default_ip(self, interface=None):
    #     """
    #     Returns the ip if the container has a default nic
    #     :return: netaddr.IPNetwork
    #     """
    #     if interface is None:
    #         for route in self.client.ip.route.list():
    #             if route['gw']:
    #                 interface = route['dev']
    #                 break
    #         else:
    #             raise LookupError('Could not find default interface')
    #     for ipaddress in self.client.ip.addr.list(interface):
    #         ip = netaddr.IPNetwork(ipaddress)
    #         if ip.version == 4:
    #             break
    #     else:
    #         raise LookupError('Failed to get default ip')
    #     return ip
    #
    # def add_nic(self, nic):
    #     self.node.client.container.nic_add(self.id, nic)
    #
    # def remove_nic(self, nicname):
    #     for idx, nic in enumerate(self.info['container']['arguments']['nics']):
    #         if nic['state'] == 'configured' and nic['name'] == nicname:
    #             break
    #     else:
    #         return
    #     self.node.client.container.nic_remove(self.id, idx)
    #
    # @property
    # def client(self):
    #     if not self._client:
    #         self._client = self.node.client.container.client(self.id)
    #     return self._client
    #
    # def upload_content(self, remote, content):
    #     if isinstance(content, str):
    #         content = content.encode('utf8')
    #     bytes = BytesIO(content)
    #     self.client.filesystem.upload(remote, bytes)
    #
    # def download_content(self, remote):
    #     buff = BytesIO()
    #     self.client.filesystem.download(remote, buff)
    #     return buff.getvalue().decode()
    #
    # def _create_container(self, timeout=60):
    #     self._log_debug("send create container command to zero-os (%s)", self.flist)
    #     tags = [self.name]
    #     if self.hostname and self.hostname != self.name:
    #         tags.append(self.hostname)
    #
    #     # Populate the correct mounts dict
    #     if type(self.mounts) == list:
    #         mounts = {}
    #         for mount in self.mounts:
    #             try:
    #                 sp = self.node.storagepools.get(mount['storagepool'])
    #                 fs = sp.get(mount['filesystem'])
    #             except KeyError:
    #                 continue
    #             mounts[fs.path] = mount['target']
    #         self.mounts = mounts
    #
    #     job = self.node.client.container.create(
    #         root_url=self.flist,
    #         mount=self.mounts,
    #         host_network=self.host_network,
    #         nics=self.nics,
    #         port=self.ports,
    #         tags=tags,
    #         name=self.name,
    #         hostname=self.hostname,
    #         storage=self.storage,
    #         privileged=self.privileged,
    #         identity=self.identity,
    #         env=self.env
    #     )
    #
    #     self._client = self.node.client.container.client(int(job.get(timeout)))
    #
    # def is_job_running(self, id):
    #     try:
    #         for _ in self.client.job.list(id):
    #             return True
    #         return False
    #     except Exception as err:
    #         if str(err).find("invalid container id"):
    #             return False
    #         raise
    #
    # def stop_job(self, id, signal=signal.SIGTERM, timeout=30):
    #     is_running = self.is_job_running(id)
    #     if not is_running:
    #         return
    #
    #     self._log_debug('stop job: %s', id)
    #
    #     self.client.job.kill(id)
    #
    #     # wait for the daemon to stop
    #     start = time.time()
    #     end = start + timeout
    #     is_running = self.is_job_running(id)
    #     while is_running and time.time() < end:
    #         time.sleep(1)
    #         is_running = self.is_job_running(id)
    #
    #     if is_running:
    #         raise RuntimeError('Failed to stop job {}'.format(id))
    #
    # def is_port_listening(self, port, timeout=60, network=('tcp', 'tcp6')):
    #     def is_listening():
    #         for lport in self.client.info.port():
    #             if lport['network'] in network and lport['port'] == port:
    #                 return True
    #         return False
    #
    #     if timeout:
    #         start = time.time()
    #         while start + timeout > time.time():
    #             if is_listening():
    #                 return True
    #             time.sleep(1)
    #         return False
    #     else:
    #         return is_listening()
    #
    #
    # @property
    # def nics(self):
    #     if self.is_running():
    #         return list(filter(lambda nic: nic['state'] == 'configured',
    #                            self.info['container']['arguments']['nics']))
    #     else:
    #         nics = []
    #         for nic in self._nics:
    #             nic.pop('state', None)
    #             nics.append(nic)
    #
    #         return nics
    #
    # def waitOnJob(self, job):
    #     MAX_LOG = 15
    #     logs = []
    #
    #     def callback(lvl, message, flag):
    #         if len(logs) == MAX_LOG:
    #             logs.pop(0)
    #         logs.append(message)
    #
    #         if flag & 0x4 != 0:
    #             erroMessage = " ".join(logs)
    #             raise RuntimeError(erroMessage)
    #     resp = self.client.subscribe(job.id)
    #     resp.stream(callback)
    #
    # def get_forwarded_port(self, port):
    #     for k, v in self.ports.items():
    #         if v == port:
    #             return int(k.split(':')[-1])
    #
    # @property
    # def mgmt_addr(self):
    #     return get_zt_ip(self.client.info.nic())


class ZOSContainers(j.application.JSBaseConfigsClass):
    _CHILDCLASS = ZOSContainer
