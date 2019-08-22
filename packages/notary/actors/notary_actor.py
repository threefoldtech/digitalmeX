from io import BytesIO

import nacl
from Jumpscale import j
from pyblake2 import blake2b

JSBASE = j.application.JSBaseClass


class RegisterError(RuntimeError):
    pass


class notary_actor(JSBASE):
    def __init__(self, *args, **kwarsg):
        self.bcdb = j.data.bcdb.get("notary_bcdb")
        self.tfchain = j.clients.tfchain.new("notary", network_type="TEST")

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
        return nacl.signing.VerifyKey(str(encoded_key), encoder=nacl.encoding.HexEncoder), record.identifier

    def register(self, threebot_id, content, content_signature, schema_out):
        """
        ```in
        threebot_id = "" (S)
        content = (bytes)
        content_signature = (bytes)
        ```
        ```out
        hash = "" (S)
        ```
        """
        try:
            verify_key, threebot_identifier = self._bot_verify_key(threebot_id)
        except j.clients.tfchain.errors.ExplorerServerError as err:
            raise RegisterError(str(err))

        _verify_signature(content, content_signature, verify_key)

        content_hash = _hash_content(threebot_identifier, content)

        model = self.bcdb.model_get_from_url("threefold.grid.notary.reservation")

        result = model.find(hash=content_hash)
        if result:
            raise KeyError(
                "reservation already exists in the notary. This should never happens, make sure you set include a unique field in your content"
            )

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
        model = self.bcdb.model_get_from_url("threefold.grid.notary.reservation")
        result = model.find(hash=hash)
        if not result:
            raise KeyError("reservation not found")
        if len(result) > 1:
            raise RuntimeError("Found more than one reservation with the same hash")

        return schema_out.new(serializeddata=j.data.serializers.jsxdata.dumps(result[0]))


def _hash_content(threebot_id, content):
    """
    return the 32 bytes blake2 hash of
    the threebot_id + encrypted reservation content

    :param content: content to hash
    :type content: bytes
    :return: hex encoded blake2 hash
    :rtype: string
    """
    if not isinstance(threebot_id, int):
        raise TypeError("threebot_id must be an int. The unique identifier of the theebot, not its same")
    if threebot_id <= 0:
        raise TypeError("threebot_id cannot be negative")

    buff = BytesIO()

    bi = _int_to_bytes(threebot_id)
    buff.write(bi)

    if isinstance(content, str):
        content = content.encode("utf-8")
    buff.write(content)
    return j.data.hash.blake2_string(buff.getvalue(), 32)


def _int_to_bytes(i):
    return i.to_bytes(64, byteorder="big")


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
