import json
from Jumpscale import j
import nacl
from pyblake2 import blake2b


JSBASE = j.application.JSBaseClass


class notary_actor(JSBASE):
    def __init__(self):
        self.bcdb = j.data.bcdb.bcdb_instances["notary_bcdb"]
        self.tfchain = j.clients.tfchain.new('notary', network_type='TEST')

    def start_page(self):
        return "welcome to https://github.com/threefoldtech/home/issues/135"

    def _bot_verify_key(self, bot_id):
        """
        retrieve the verify key of the threebot identified by bot_id
        from tfchain

        :param bot_id: threebot identification, can be one of the name or the unique integer
                        of a threebot
        :type bot_id: string
        :return: verify key we can use to verify message signed by the threebot
        :rtype: nacl.singing.VerfiyKey
        """
        record = self.tfchain.threebot.record_get(bot_id)
        encoded_key = record.public_key.hash
        return nacl.signature.VerifyKey(
            str(encoded_key),
            encoder=nacl.encoding.HexEncoder)

    def register(self, threebot_id, content, content_signature, schema_out):
        """
        ```in
        threebot_id = "" (S)
        content = "" (bytes)
        content_signature = (bytes)
        ```
        ```out
        hash = "" (S)
        ```
        """
        verify_key = self._bot_verify_key(threebot_id)
        _verify_signature(content, content_signature, verify_key)

        model = self.bcdb.models.get("threefold.grid.notary.reservation")

        content_hash = _hash_content(content)

        model_obj = model.new()
        model_obj.hash = content_hash
        model_obj.threebot_id = threebot_id
        model_obj.content = content
        model_obj.content_signature = content_signature
        model_obj.save()

        out = schema_out.new()
        out.hash = content_hash
        return out

    def get(self, hash, schema_out):
        """
        ```in
        hash = "" (S)
        ```
        ```out
        !threefold.grid.notary.reservation
        ```
        """
        model = self.bcdb.models.get("threefold.grid.notary.reservation")
        return model.get(hash=hash)


def _hash_content(content):
    """
    return the 32 bytes blake2 hash  of content

    :param content: content to hash
    :type content: bytes
    :return: hex encoded blake2 hash
    :rtype: string
    """
    return j.data.blake2_string(content, size=32)


def _verify_signature(smessage, signature, verify_key):
    """
    verify the signature for the signed message is valid

    :param smessage: the signed message
    :type smessage: bytes
    :param signature: the signature of smessage
    :type signature: bytes
    :param verify_key: the verify key
    :type verify_key: nacl.signing.VerifyKey
    :raises nacl.exceptions.BadSignature: raised if the verification of the signature failed
    """
    verify_key.verify(smessage, signature)
