from Jumpscale import j

from .GedisClient import GedisClient

JSConfigBase = j.application.JSBaseConfigsClass


class ThreebotClientFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.clients.gedis"
    _CHILDCLASS = GedisClient
