from Jumpscale import j
import json
from dns.resolver import Answer

class DNSItem():

    def __init__(self):
        schema_text = """
        @url = jumpscale.dnsItem.1
        name* = ""
        domain = "" (S)
        record_type = "A,AAAA,CNAME,TXT,NS,MX,SRV,SOA" (E)
        value = "127.0.0.1" (S)
        ttl = 100 (I)
        priority = 10 (I)
        """
        zdb_admin = j.clients.zdb.client_admin_get(port=9901)
        zdb = zdb_admin.namespace_new("dns")
        bcdb = j.data.bcdb.new("dns", zdbclient=zdb)
        schema_text = j.core.text.strip(schema_text)
        schema = j.data.schema.get(schema_text)
        self.model = bcdb.model_get_from_schema(schema)


    def create_item(self, name="", domain="", record_type='A', value="127.0.0.1" , ttl=100, priority=10):
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
        obj = self.model.new()
        obj.domain = domain or domain
        obj.record_type = record_type or obj.record_type
        obj.value = value or obj.value
        obj.ttl = ttl or obj.ttl
        obj.priority = priority or obj.priority
        obj.name = "%s_%s" % (obj.domain,obj.record_type)
        obj.save()

    def get_item(self, domain, record_type="A"):
        '''Get dns object from db using bcdb with query name as (domain)_(record_type)

        :param domain: domain name of entry
        :type domain: str
        :param record_type: dns type
        :type record_type: str
        :return: object model found in db
        :rtype: 
 
        '''
        name = "%s_%s" % (domain, record_type)
        obj = self.model.get_by_name(name)
        return obj[0] if obj else None
