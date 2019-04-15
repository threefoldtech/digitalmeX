from Jumpscale import j
import json
from dns.resolver import Answer

class DNSItem():

    def __init__(self):
        schema_text = """
        @url = jumpscale.dnsItem.1
        name* = ""
        domain = "" (S)
        type_dns = "A" (S)
        ip_address = "127.0.0.1" (ipaddr)
        ttl = 100 (I)
        """
        bcdb = j.data.bcdb.new("dns")
        schema_text = j.core.text.strip(schema_text)
        schema = j.data.schema.get(schema_text)
        self.model = bcdb.model_get_from_schema(schema)


    def create_item(self, name="", domain="", type_dns='A', ip_address="127.0.0.1" , ttl=100):
        '''Create a new dns object and save to db using bcdb

        :param domain: domain name of entry
        :type domain: str
        :param type_dns: dns type
        :type type_dns: str
        :param ip_address: IP address of entry
        :type ip_address: str
        :param ttl: time to live
        :type ttl: int
        '''
        # Create a new object from the model
        obj = self.model.new()
        obj.domain = domain or domain
        obj.type_dns = type_dns or obj.type_dns
        obj.ip_address = ip_address or obj.ip_address
        obj.ttl = ttl or obj.ttl
        obj.name = "%s_%s" % (obj.domain,obj.type_dns)
        obj.save()

    def get_item(self, domain, type_dns="A"):
        '''Get dns object from db using bcdb with query name as (domain)_(type_dns)

        :param domain: domain name of entry
        :type domain: str
        :param type_dns: dns type
        :type type_dns: str
        :return: object model found in db
        :rtype: 
 
        '''
        name = "%s_%s" % (domain, type_dns)
        obj = self.model.get_by_name(name)
        return obj[0] if obj else None
