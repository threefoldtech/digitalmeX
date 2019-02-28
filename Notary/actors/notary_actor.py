
import json
from Jumpscale import j


JSBASE = j.application.JSBaseClass


class notary_actor(JSBASE):

    def start_page(self):
        return "welcome to https://github.com/threefoldtech/home/issues/135"

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
        # TODO: return json object
        out.message = "your key is {}".format(key)
        return out

    def delete(self, robot_id, key, key_signature, schema_out):
        """
        ```in
        robot_id = "" (S)
        key = "" (S)
        key_signature = "" (S)
        ```
        ```out
        message = "" (S)
        ```
        """
        out = schema_out.new()
        # TODO: return true if success deleted from zdb otherwise return false
        return "False"
