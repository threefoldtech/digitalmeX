from Jumpscale import j


def main(self):

    # raise RuntimeError()
    j.servers.zdb.start_test_instance()

    # Load schema used for testing to the client process
    schema_text = """
    @url = jumpscale.example.wallet
    jwt = "" (S)                # JWT Token
    addr* = ""                   # Address
    ipaddr = (ipaddr)           # IP Address
    email = "" (S)              # Email address
    username = "" (S)           # User name
    """

    init_script = """
# loading the schema used for testing in the server process
schema_text = \"\"\"
{}
\"\"\"
j.data.schema.get(schema_text)
# starting the server
gedis = j.servers.gedis.configure(name="test", port=8888, host="127.0.0.1", ssl=False, password="123456")
gedis.save()
gedis.actor_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/extra/examples/actors/gedis_examples.py", "gedis_examples")
gedis.start()
    """.format(schema_text)
    print("START GEDIS IN TMUX")
    cmd = "js_shell '{}'".format(init_script)
    j.tools.tmux.execute(
        cmd,
        window='gedis_test',
        pane='main',
        reset=False,
    )

    res = j.sal.nettools.waitConnectionTest("localhost", 8888, timeoutTotal=30)
    if res == False:
        raise RuntimeError("Could not start gedis server on port:%s" % 8888)
    self._log_info("gedis server '%s' started" % 8888)
    print("[*] testing echo")
    cl = j.clients.gedis.get("test", port=8888, namespace='gedis_examples')
    assert cl.cmds.gedis_examples.echo("s") == b"s"
    print("- done")
    # print("[*] testing set with schemas")
    # # print("[1] schema_in as schema url")
    # #
    # # wallet_out1 = cl.gedis_examples.example1(addr="testaddr")
    # # assert wallet_out1.addr == "testaddr"
    # # print("[1] Done")
    print("[2] schema_in as inline schema with url")
    wallet_schema = j.data.schema.get(url="jumpscale.example.wallet")
    wallet_in = wallet_schema.new()
    wallet_in.addr = "testaddr"
    wallet_in.jwt = "testjwt"
    wallet_out = cl.cmds.gedis_examples.example2(wallet_in)

    assert wallet_in.addr == wallet_out.addr
    assert wallet_in.jwt == wallet_out.jwt
    print("[2] Done")

    print("[3] inline schema in and inline schema out")
    res = cl.cmds.gedis_examples.example3(a='a', b=True, c=2)
    assert res.a == 'a'
    assert res.b is True
    assert res.c == 2

    print("[3] Done")
    print("[4] inline schema for schema out with url")
    res = cl.cmds.gedis_examples.example4(wallet_in)
    assert res.result.addr == wallet_in.addr
    assert res.custom == "custom"
    print("[4] Done")

    print("[5] testing ping")
    s = j.clients.gedis.get("system", port=cl.port, namespace="system", secret="123456")

    assert s.cmds.system.ping().lower() == b"pong"
    print("[5] Done")

    print("**DONE**")

