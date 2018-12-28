from Jumpscale import j


class ZOSContainer(j.application.JSBaseConfigClass):

    _SCHEMATEXT = """
    @url = jumpscale.clients.zoscmd.zoscontainer.1
    name = "" (S)
    ssh_addr = "127.0.0.1" (S)
    ssh_port = 22 (S)
    """

    def _init(self):
        self.ZOSNode = None  #links to the ZOSNode which hosts this ZOSContainer

    @property
    def zos_client(self):
        """
        return zos protocol client
        :return:
        """
        pass
        #implement caching at client side

    def ssh_client(self):
        """

        :return: ssh client to this container
        """
        pass
        #implement caching at client side

    def start(self):
        self.cache.delete("stop") #make sure that we will redo the stop action
        def do():
            pass
            #implement the logic how to start the container
        if not self.running(refresh=True,timeout=0):
            self.cache.get(key="start", method=do, refresh=True, die=True)
        assert self.running() == True

    def stop(self):
        """
        stop the container
        :return:
        """
        self.cache.delete("start") #make sure that we will redo the stop action
        self.cache.delete("running")
        def do():
            pass
        self.cache.get(key="stop", method=do, refresh=True, die=True)
        assert self.running() == False

    def running(self,timeout=60, refresh=True):
        """
        check container is running only using zos client
        :return:
        """
        def do():
            pass
        self.cache.get(key="running", method=do, timeout=timeout,refresh=refresh,expire=10, die=True)
        #expiration 0 means will always check again, sometimes makes sense to not recheck e.g. in 5 sec
        #refresh can be overruled so will check everytime (only relevant to use when expire is not 0)

        pass

    def reset(self):
        """
        remove all data (if there would be persistence in zos container)
        :return:
        """
        self.cache.reset() #all cached states need to go
        #TODO:

        pass

    def test(self):
        pass
        #do a basic test, look for client (e.g. start an ubuntu 18.04 container)
        #make connection
        #some test

    @property
    def _info(self):
        self._logger.debug("get container info")
        for containerid, container in self.node.client.container.list().items():
            if self.name == container['container']['arguments']['name']:
                containerid = int(containerid)
                if self._client and self._client.container != containerid:
                    self._client = None
                container['container']['id'] = int(containerid)
                return container
        return

    # def from_containerinfo(cls, containerinfo, node, logger=None):
    #     logger = logger or default_logger
    #     logger.debug("create container from info")
    #
    #     arguments = containerinfo['container']['arguments']
    #     return cls(name=arguments['name'],
    #                node=node,
    #                flist=arguments['root'],
    #                hostname=arguments['hostname'],
    #                mounts=arguments['mount'],
    #                nics=arguments['nics'],
    #                host_network=arguments['host_network'],
    #                ports=arguments['port'],
    #                storage=arguments['storage'],
    #                privileged=arguments['privileged'],
    #                identity=arguments['identity'],
    #                env=arguments['env'],
    #                logger=logger)

    @property
    def id(self):
        self._logger.debug("get container id")
        info = self.info
        if info:
            return info['container']['id']
        return

    @property
    def info(self):
        self._logger.debug("get container info")
        for containerid, container in self.node.client.container.list().items():
            if self.name == container['container']['arguments']['name']:
                containerid = int(containerid)
                if self._client and self._client.container != containerid:
                    self._client = None
                container['container']['id'] = int(containerid)
                return container
        return

    @property
    def identity(self):
        if not self._identity:
            if self.is_running():
                for nic in self.nics:
                    if nic['type'] == 'zerotier':
                        self._identity = self.client.zerotier.info()['secretIdentity']
        return self._identity

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
            interfaces = [l['name'] for l in self.client.ip.link.list() if l['name'] not in ['lo']]

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
                if route['gw']:
                    interface = route['dev']
                    break
            else:
                raise LookupError('Could not find default interface')
        for ipaddress in self.client.ip.addr.list(interface):
            ip = netaddr.IPNetwork(ipaddress)
            if ip.version == 4:
                break
        else:
            raise LookupError('Failed to get default ip')
        return ip

    def add_nic(self, nic):
        self.node.client.container.nic_add(self.id, nic)

    def remove_nic(self, nicname):
        for idx, nic in enumerate(self.info['container']['arguments']['nics']):
            if nic['state'] == 'configured' and nic['name'] == nicname:
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
            content = content.encode('utf8')
        bytes = BytesIO(content)
        self.client.filesystem.upload(remote, bytes)

    def download_content(self, remote):
        buff = BytesIO()
        self.client.filesystem.download(remote, buff)
        return buff.getvalue().decode()

    def _create_container(self, timeout=60):
        self._logger.debug("send create container command to zero-os (%s)", self.flist)
        tags = [self.name]
        if self.hostname and self.hostname != self.name:
            tags.append(self.hostname)

        # Populate the correct mounts dict
        if type(self.mounts) == list:
            mounts = {}
            for mount in self.mounts:
                try:
                    sp = self.node.storagepools.get(mount['storagepool'])
                    fs = sp.get(mount['filesystem'])
                except KeyError:
                    continue
                mounts[fs.path] = mount['target']
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
            env=self.env
        )

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

    def stop_job(self, id, signal=signal.SIGTERM, timeout=30):
        is_running = self.is_job_running(id)
        if not is_running:
            return

        self._logger.debug('stop job: %s', id)

        self.client.job.kill(id)

        # wait for the daemon to stop
        start = time.time()
        end = start + timeout
        is_running = self.is_job_running(id)
        while is_running and time.time() < end:
            time.sleep(1)
            is_running = self.is_job_running(id)

        if is_running:
            raise RuntimeError('Failed to stop job {}'.format(id))

    def is_port_listening(self, port, timeout=60, network=('tcp', 'tcp6')):
        def is_listening():
            for lport in self.client.info.port():
                if lport['network'] in network and lport['port'] == port:
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

    def start(self):
        if not self.is_running():
            self._logger.debug("start %s", self)
            self._create_container()
            for process in self.init_processes:
                cmd = "{} {}".format(process['name'], ' '.join(process.get('args', [])))
                pwd = process.get('pwd', '')
                stdin = process.get('stdin', '')
                id = process.get('id')
                env = {}
                for x in process.get('environment', []):
                    k, v = x.split("=")
                    env[k] = v
                self.client.system(command=cmd, dir=pwd, stdin=stdin, env=env, id=id)

    def stop(self):
        """
        will stop the container and also his mountpoints
        :return:
        """
        if not self.is_running():
            return
        self._logger.debug("stop %s", self)

        self.node.client.container.terminate(self.id)
        self._client = None

    def is_running(self):
        return self.node.is_running() and self.id is not None

    @property
    def nics(self):
        if self.is_running():
            return list(filter(lambda nic: nic['state'] == 'configured',
                               self.info['container']['arguments']['nics']))
        else:
            nics = []
            for nic in self._nics:
                nic.pop('state', None)
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
                return int(k.split(':')[-1])

    @property
    def mgmt_addr(self):
        return get_zt_ip(self.client.info.nic())

    
    def __str__(self):
        return j.core.tools.text_replace("{RED}zoscontainer{RESET}:%-14s %-25s:%-4s" % (self.name, self.addr,self.port))

    __repr__ = __str__
