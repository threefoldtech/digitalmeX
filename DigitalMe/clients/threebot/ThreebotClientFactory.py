from Jumpscale import j
import binascii
from .ThreebotClient import ThreebotClient

JSConfigBase = j.application.JSBaseConfigsClass


class ThreebotClientFactory(j.application.JSBaseConfigsClass):
    __jslocation__ = "j.clients.threebot"
    _CHILDCLASS = ThreebotClient

    def _init(self, **kwargs):
        self._explorer = None

    @property
    def explorer(self):
        if not self._explorer:
            self._explorer = self.get(name="explorer", host="134.209.90.92")
        return self._explorer

    def sign(self, payload):
        n = j.data.nacl.get()
        return n.signing_key.sign(payload)

    def threebot_record_get(self, user_id=None, name=None):
        r = self.explorer.client.actors.phonebook.get(user_id=user_id, name=name)
        j.shell()

    def threebot_register(self, name, email, ipaddr="", description="", pubkey=None):
        n = j.data.nacl.get()
        if not pubkey:
            pubkey = n.verify_key.encode()
        self._log(pubkey)

        # FOR ENCRYPTION WITH PUB KEY
        # import nacl
        # from nacl.signing import VerifyKey
        #
        # vk = VerifyKey(pubkey)
        # pubkey_obj = vk.to_curve25519_public_key()
        # encrypted = n.encrypt(b"a", hex=False, public_key=pubkey_obj)
        # n.decrypt(encrypted)

        j.shell()

        if isinstance(pubkey, bytes):
            pubkey = binascii.hexlify(pubkey).decode()
        else:
            raise j.exceptions.Input("needs to be bytes")

        payload = name + email + pubkey + ipaddr + description
        signature = self.sign(payload.encode())

        # need to show how to use the pubkey to verify the signature & get the data

        pubkey_binary = binascii.unhexlify(pubkey)
        self._log(pubkey_binary)
        assert n.verify(payload.encode(), signature, verify_key=pubkey_binary)
        j.shell()
        w
        import nacl

        r = self.explorer.client.actors.phonebook.register(name=name, email=email, pubkey=pubkey, signature=signature)

        j.shell()

    def test(self):
        """
        kosmos 'j.clients.threebot.test()'
        :return:
        """

        r = self.threebot_register("test.test", "test@incubaid.com", ipaddr="134.209.90.92")
        j.shell()
