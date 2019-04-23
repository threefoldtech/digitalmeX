from unittest import TestCase
from uuid import uuid4
from Jumpscale import j
import os 
os.chdir('/sandbox/code/github/threefoldtech/digitalmeX/packages/gdrive/tests')


class Basetest(TestCase):

        
    def log(self, msg):
        j.core.tools.log(msg, level=20)

    def random_string(self):
        return str(uuid4())[:10]

    @classmethod
    def setUpClass(cls):
        gedis_cmd = """
        ln -s /sandbox/code/github/threefoldtech/digitalmeX/packages/gdrive/app.moon /sandbox/code/github/threefoldfoundation/lapis-wiki/applications/gdrive.moon;
        ln -s /sandbox/var/gdrive/static/ /sandbox/code/github/threefoldfoundation/lapis-wiki/static/gdrive;
        kosmos 'g_client = j.clients.gdrive.get();\
                g_client.credfile = "cred.json";\
                server = j.servers.gedis.get("test", port=8888);\
                server.actor_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/gdrive/actors/gdrive.py", "default");\
                server.start()'
        """ 
        path = j.tools.path.get('.')
        cls.gedis = j.tools.startupcmd.get(name='gedis', cmd=gedis_cmd, path=path.abspath())
        cls.gedis.start()
        cmd = 'moonc . && lapis server'
        path = '/sandbox/code/github/threefoldfoundation/lapis-wiki'
        cls.moon = j.tools.startupcmd.get(name='server', cmd=cmd, path=path)
        cls.moon.start()

    @classmethod
    def tearDownClass(cls):
        cls.gedis.stop()
        cls.moon.stop()
        j.sal.process.killall('nginx')
