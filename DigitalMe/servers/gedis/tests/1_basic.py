from Jumpscale import j


def main(self):

    # raise RuntimeError()
    zdb = j.servers.zdb.start_test_instance()

    j.shell()

    gedis = self.configure(name="test", port=8888, host="localhost", ssl=False,
                           password="123456", interactive=False)

    print("START GEDIS IN TMUX")
    cmd = "js_shell 'j.servers.gedis.test_server_start()'"
    j.tools.tmux.execute(
        cmd,
        window='gedis_test',
        pane='main',
        reset=False,
    )

    res = j.sal.nettools.waitConnectionTest("localhost", int(gedis.port), timeoutTotal=1000)
    if res == False:
        raise RuntimeError("Could not start gedis server on port:%s" % int(gedis.port))
    self._log_info("gedis server '%s' started" % gedis.name)
    print("[*] testing echo")

    cl = gedis.client_get(namespace="gedis_examples")
    assert cl.gedis_examples.echo("s") == b"s"
    print("- done")
    print("[*] testing set with schemas")
    # print("[1] schema_in as schema url")
    #
    # wallet_out1 = cl.gedis_examples.example1(addr="testaddr")
    # assert wallet_out1.addr == "testaddr"
    # print("[1] Done")
    print("[2] schema_in as inline schema with url")
    wallet_schema = j.data.schema.get("jumpscale.example.wallet")
    wallet_in = wallet_schema.new()
    wallet_in.addr = "testaddr"
    wallet_in.jwt = "testjwt"
    wallet_out = cl.gedis_examples.example2(wallet_in)

    assert wallet_in.addr == wallet_out.addr
    assert wallet_in.jwt == wallet_out.jwt
    print("[2] Done")

    print("[3] inline schema in and inline schema out")
    res = cl.gedis_examples.example3(a='a', b=True, c='2')
    assert res.a == 'a'
    assert res.b is True
    assert res.c == 2

    print("[3] Done")
    print("[4] inline schema for schema out with url")
    res = cl.gedis_examples.example4(wallet_in)
    assert res.result.addr == wallet_in.addr
    assert res.custom == "custom"
    print("[4] Done")

    s = j.clients.gedis.configure("system", port=cl.port, namespace="system", secret="123456")

    assert s.system.ping().lower() == b"pong"

    print("**DONE**")

