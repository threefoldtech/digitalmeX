
import json
from Jumpscale import j


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
        model_obj = model.new()
        model_obj.threebot_id = threebot_id
        model_obj.key = key
        model_obj.content = content
        model_obj.content_signature = content_signature
        model_obj.save()

        out.message = "your register info is threebot_id = {} , key = {}, content = {} ,content_signature ={}".format(
            threebot_id, key, content, content_signature)
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
                return model

        out.message = "this key doesn't exist"
        return out

    def delete(self, threebot_id, key, content_signature, schema_out):
        """
        ```in
        threebot_id = "" (S)
        key = "" (S)
        content_signature = "" (S)
        ```
        ```out
        message = "" (S)
        ```
       """
        out = schema_out.new()
        bcdb = self.bcdb
        for model in bcdb.get_all():
            if model.key == key and model.threebot_id == threebot_id and model.content_signature == content_signature:
                model.delete()
                model.save()
                out.message = "True"
                return out
        out.message = "False"
        return out
