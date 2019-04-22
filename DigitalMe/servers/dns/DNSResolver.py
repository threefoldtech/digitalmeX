from Jumpscale import j
import json
from dns.resolver import Answer


class DNSResolver:

    def __init__(self, bcdb):
        schema_text = """
        @url = jumpscale.dnsItem.1
        name* = ""
        domain = "" (S)
        record_type = "A,AAAA,CNAME,TXT,NS,MX,SRV,SOA" (E)
        value = "127.0.0.1" (S)
        ttl = 100 (I)
        priority = 10 (I)
        """
        schema_text = j.core.text.strip(schema_text)
        schema = j.data.schema.get(schema_text)
        self.model = bcdb.model_get_from_schema(schema)

    def create_item(self, domain="", record_type='A', value="127.0.0.1", ttl=100, priority=10):
        '''Create a new dns object and save to db using bcdb

        :param domain: domain name of entry
        :type domain: str
        :param record_type: dns type
        :type record_type: str
        :param value: IP address of entry
        :type value: str
        :param ttl: time to live
        :type ttl: int
        :param priority: (optional) priority when record type is MX or SRV
        :type priority: int
        '''
        # Create a new object from the model
        name = "%s_%s" % (domain, record_type)
        obj = self.model.get_by_name(name)
        if obj:
            obj = obj[0]
        else:
            obj = self.model.new()
        obj.domain = domain
        obj.record_type = record_type
        obj.value = value
        obj.ttl = ttl
        obj.priority = priority
        obj.name = name
        obj.save()

    def get_item(self, domain, record_type="A"):
        """
        Get dns object from db using bcdb with query name as (domain)_(record_type)
        :param domain: domain name of entry
        :type domain: str
        :param record_type: dns type
        :type record_type: str
        :return: object model found in db
        :rtype:
        """
        name = "%s_%s" % (domain, record_type)
        obj = self.model.get_by_name(name)
        if obj:
            return obj[0]
        else:
            domain_parts = domain.split(".")
            if len(domain_parts) > 2:
                domain_parts.pop(0)
                domain = ".".join(domain_parts)
                return self.get_item(domain, record_type)
            else:
                return None
