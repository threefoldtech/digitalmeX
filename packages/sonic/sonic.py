from Jumpscale import j


class sonic(j.application.JSBaseClass):

    def _init(self):
        self.sonic_client = j.clients.sonic.get()

    def query(self, collection, bucket, text, schema_out):
        """
        ```in
        collection = "" (S)
        bucket = "" (S)
        text = "" (S)
        ```
        ```out
        res = (LS)
        ```
        :param collection:
        :param bucket:
        :param text:
        :return:
        """
        out = schema_out.new()
        out.res = self.sonic_client.query(collection, bucket, text)
        return out
