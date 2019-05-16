from Jumpscale import j
import sys

JSBASE = j.application.JSBaseClass


schema_text = """
    @url = jumpscale.kds
    jwt = "" (S)                # JWT Token
    addr* = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    """

schema_text2 = """
    @url = jumpscale.example.wallet
    jwt = "" (S)                # JWT Token
    addr* = ""                  # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    """
j.data.schema.get_from_text(schema_text)
j.data.schema.get_from_text(schema_text2)


class painter(JSBASE):
    """
    """

    def echo(self, msg):
        return msg

    def count(self, a, b):
        return int(a) + int(b)

    def example1(self, addr, schema_out):
        """
        ```out
        !jumpscale.example.wallet
        ```
        """
        w = schema_out.new()
        w.addr = addr
        return w

    def example2(self, wallet, schema_out):
        """
        ```in
        wallet = (O) !jumpscale.example.wallet
        ```

        ```out
        !jumpscale.example.wallet
        ```

        """
        w = wallet
        return w

    def example3(self, a, b, c, schema_out):
        """
        ```in
        a = (S)
        b = (B)
        c = (I)
        ```

        ```out
        a = (S)
        b = (B)
        c = (I)
        ```
        """
        w = schema_out.new()
        w.a = a
        w.b = not b
        w.c = c
        return w

    def example4(self, wallet, schema_out):
        """
        ```in
        wallet = (O) !jumpscale.example.wallet
        ```

        ```out
        result = (O) !jumpscale.example.wallet
        custom = (S)
        ```
        """
        w = schema_out.new()
        w.result.ipaddr = wallet.ipaddr
        w.result.addr = wallet.addr
        w.result.jwt = wallet.jwt
        w.custom = "custom"
        return w
