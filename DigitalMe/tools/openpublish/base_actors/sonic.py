from Jumpscale import j

JSBASE = j.application.JSBaseClass

## TODO: code to check if ingest_client, search_client are configured already or not.
class sonic(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

    def push(self, collection, bucket, objectName, text):
        cl = j.clients.sonic.get("ingest_client")
        with cl.client as ingest_client:
            return ingest_client.push(collection, bucket, objectName, text)

    def search(self, collection, bucket, terms):
        cl = j.clients.sonic.get("search_client")
        with cl.client as search_client:
            return search_client.query(collection, bucket, terms)

