from Jumpscale import j

serverscript = '''

# starting the server
gedis = j.servers.gedis.configure(name="test", port=8888, host="127.0.0.1", ssl=False, password="123456")
gedis.save()
gedis.actors_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/extra/examples/actors", "ibiza")
gedis.start()

'''


def main(self):
    """
    kosmos 'j.servers.gedis.test("basic")'
    """

    # j.servers.zdb.start_test_instance()

    def start():
        #Load schema used for testing to the client process
        cmd = j.tools.startupcmd.get("gedis_test", serverscript, cmd_stop='', path='/tmp', timeout=30,
                                     env={}, ports=[8888], process_strings=[], interpreter='jumpscale', daemon=True)
        cmd.start()

        res = j.sal.nettools.waitConnectionTest("localhost", 8888, timeoutTotal=30)
        if res == False:
            raise RuntimeError("Could not start gedis server on port:%s" % 8888)
        self._log_info("gedis server '%s' started" % 8888)

    start()

    print("[*] testing echo")
    client = j.clients.gedis.get("gedis_test", port=8888, namespace='ibiza')

    client.actors

    # assert client.actors.painter.echo("s") == b"s"
    print("- done")
    print("[*] testing set with schemas")


    print("[1] schema_in as schema url")
    wallet_out1 = client.actors.painter.example1(addr="testaddr")
    assert wallet_out1.addr == "testaddr"
    print("[1] Done")

    print("[2] schema_in as inline schema with url")
    wallet_schema = j.data.schema.get_from_url_latest(url="jumpscale.example.wallet")
    wallet_in = wallet_schema.new()
    wallet_in.addr = "testaddr"
    wallet_in.jwt = "testjwt"

    wallet_out = client.actors.painter.example2(wallet_in)

    assert wallet_in.addr == wallet_out.addr
    assert wallet_in.jwt == wallet_out.jwt
    print("[2] Done")

    print("[3] inline schema in and inline schema out")
    res = client.actors.painter.example3(a='a', b=True, c=2)
    assert res.a == 'a'
    assert res.b is True
    assert res.c == 2

    print("[3] Done")
    print("[4] inline schema for schema out with url")
    res = client.actors.painter.example4(wallet_in)
    assert res.result.addr == wallet_in.addr
    assert res.custom == "custom"
    print("[4] Done")

    print("[5] testing ping")
    s = j.clients.gedis.get("system", port=client.port, namespace="system", secret="123456")

    assert s.actors.system.ping().lower() == b"pong"

    assert client.actors.painter.echo("s") == b"s"


    print("[5] Done")

    print("**DONE**")
