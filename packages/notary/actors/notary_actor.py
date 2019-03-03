
import json
from Jumpscale import j


JSBASE = j.application.JSBaseClass


class notary_actor(JSBASE):

    def start_page(self):
        return "welcome to https://github.com/threefoldtech/home/issues/135"

    def bcdb_get(self):
        zdb_cl = j.clients.zdb.start_test_instance()
        zdb_cl = zdb_cl.namespace_new("notary_namespace", secret="1234")
        bcdb = j.data.bcdb.new(zdbclient=zdb_cl, name="notary_bcdb")
        bcdb.models_add("/sandbox/code/github/threefoldtech/digitalmeX/packages/notary/models")
        return bcdb

    def register(self, robot_id, key, content, content_signature, schema_out):
        """
        ```in
        robot_id = "" (S)
        key = "" (S)
        content = "" (S)
        content_signature = (S)
        ```
        ```out
        message = "" (S)
        ```
        """
        out = schema_out.new()
        bcdb = self.bcdb_get()
        model = bcdb.models.get("threefold.grid.notary")
        model_obj = model.new()
        model_obj.robot_id = robot_id
        model_obj.key = key
        model_obj.content = content
        model_obj.content_signature = content_signature
        model_obj.save()

        out.message = "your register info is robot_id = {} , key = {}, content = {} ,content_signature ={}".format(
            robot_id, key, content, content_signature)
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
        bcdb = self.bcdb_get()
        for model in bcdb.get_all():
            if model.key == key:
                return model

        out.message = "this key doesn't exist"
        return out

    def delete(self, robot_id, key, content_signature, schema_out):
        """
        ```in
        robot_id = "" (S)
        key = "" (S)
        content_signature = "" (S)
        ```
        ```out
        message = "" (S)
        ```
       """
        bcdb = self.bcdb_get()
        for model in bcdb.get_all():
            if model.key == key and model.robot_id == robot_id and model.content_signature == content_signature:
                model.delete()
                model.save()
                return "True"
        return "False"
