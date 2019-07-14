from pprint import pprint

from Jumpscale import j

from .DNSServer import DNSServer
import os

JSBASE = j.application.JSBaseClass
from .DNSServer import DNSServers
from .DNSResolver import DNSResolvers

# http://mirror1.malwaredomains.com/files/justdomains  domains we should not query, lets download & put in redis core
# https://blog.cryptoaustralia.org.au/2017/12/05/build-your-private-dns-server/


class DNSServerFactory(j.application.JSBaseConfigsFactoryClass):

    _CHILDCLASSES = [DNSServers, DNSResolvers]
    __jslocation__ = "j.servers.dns"

    def _init(self, **kwargs):
        self._extensions = {}

    def get_gevent_server(self, name="default", port=53, bcdb_name="system", resolvername="default"):
        s = self.servers.new(name=name, port=port, bcdb_name=bcdb_name, resolvername=resolvername)
        # make sure there is a resolver created
        if resolvername == "default" and self.resolvers.exists(name=resolvername) == False:
            r = self.resolvers.new(name="default")
            r.save()
        s.save()
        return s

    def start(self, port=53, background=False):

        if not background:

            rack = j.servers.rack.get()

            server = self.get_gevent_server(port=port)

            rack.add("dns", server)

            rack.start()

        else:
            # the MONKEY PATCH STATEMENT IS NOT THE BEST, but prob required for now
            S = """
            from gevent import monkey
            monkey.patch_all(subprocess=False)
            from Jumpscale import j
            j.servers.dns.start(port={port})
            """
            args = {"port": port}
            S = j.core.tools.text_replace(S, args)

            s = j.servers.startupcmd.new(name="dnsserver")
            s.cmd_start = S
            s.executor = "tmux"
            s.interpreter = "python"
            s.timeout = 10
            s.ports_udp = [port]
            s.start(reset=True)

    @property
    def dns_extensions(self):
        """
        all known extensions on http://data.iana.org/TLD/tlds-alpha-by-domain.txt
        """
        if self._extensions == {}:
            path = os.path.join(os.path.dirname(__file__), "knownextensions.txt")
            for line in j.sal.fs.readFile(path).split("\n"):
                if line.strip() == "" or line[0] == "#":
                    continue
                self._extensions[line] = True
        return self._extensions

    def test(self, start=True, port=5354):
        """
        kosmos 'j.servers.dns.test()'
        kosmos 'j.servers.dns.test(start=False)'
        """

        if start or not self.ping(port=port):
            self.start(background=True, port=port)

        ns = j.tools.dnstools.get(["localhost"], port=port)

        pprint(ns.namerecords_get("google.com"))
        pprint(ns.namerecords_get("info.despiegk"))
