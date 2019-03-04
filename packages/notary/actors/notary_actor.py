
import json
from Jumpscale import j
from pyblake2 import blake2b

JSBASE = j.application.JSBaseClass


class notary_actor(JSBASE):
    def __init__(self):

        self.bcdb = j.data.bcdb.bcdb_instances["notary_bcdb"]

    def start_page(self):
        return "welcome to https://github.com/threefoldtech/home/issues/135"

    def register(self, threebot_id, key, content, content_signature, schema_out):
        """
        ```in
        threebot_id = "" (S)
        key = "" (S)
        content = "" (S)
        content_signature = (S)
        ```
        ```out
        message = "" (S)
        ```
        """
        out = schema_out.new()
        bcdb = self.bcdb
        model = bcdb.models.get("threefold.grid.notary")
        # TODO: check that signature is inline with 3Bot ID provided, meaning the Notary verifies that the 3bot with the ID sent has indeed created the info
        model_obj = model.new()
        model_obj.threebot_id = threebot_id
        model_obj.key = key
        model_obj.content = content
        model_obj.content_signature = content_signature
        model_obj.save()

        content_hash = blake2b(str(model_obj).encode(), digest_size=10).hexdigest()
        out.message = "Hash of the content is {}".format(content_hash)
        return out

    def get(self, key, schema_out):
        """
        ```in
        key = "" (S)
        ```
        ```out
        message = "" (S)
        ```
        """
        out = schema_out.new()
        bcdb = self.bcdb
        for model in bcdb.get_all():
            if model.key == key:
                out.message = "key:{} , content:{} , threebot_id:{} , content_signature:{}".format(
                    model.key, model.content, model.threebot_id, model.content_signature)
                return out

        out.message = "this key doesn't exist"
        raise Exception(out.message)
