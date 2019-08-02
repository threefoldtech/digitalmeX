from Jumpscale import j


class sonic(j.application.JSBaseClass):
    def _init(self, **kwargs):
        self.sonic_client = j.clients.sonic.default

    def query(self, text, schema_out):
        """
        ```in
        text = "" (S)
        ```
        ```out
        res = (LS)
        ```
        :param text: text to search for in all files
        :return:
        """
        out = schema_out.new()
        out.res = j.sal.bcdbfs.search(text)
        return out
