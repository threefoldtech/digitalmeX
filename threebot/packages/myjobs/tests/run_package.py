from Jumpscale import j


def run_server():
    """just for quick testing of how to run this package

    `kosmos run_package.py`

    should add "<container_ip>  myjobs.dev" to /etc/hosts to test
    then go to
    https://myjobs.dev/myjobs/index.html

    """
    server = j.servers.threebot.get("mine")
    server.save()

    package = j.tools.threebotpackage.get(
        "myjobs", path=j.sal.fs.getParent(j.sal.fs.getDirName(__file__)), threebotserver_name="mine"
    )
    package.prepare()
    package.save()
    server.start()


run_server()
