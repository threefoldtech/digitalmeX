
import json
import os
from Jumpscale import j


JSBASE = j.application.JSBaseClass


class userbot(JSBASE):
    """
    """

    def __init__(self):
        JSBASE.__init__(self)
        self._user_bot_model = None
        self._bcdb = j.data.bcdb.new(
            name="userbotsettings")
        self._bcdb.models_add(
            "/sandbox/code/github/threefoldtech/digitalmeX/packages/init_bot/models")

    @property
    def user_bot_model(self):
        if not self._user_bot_model:
            self._user_bot_model = self._bcdb.model_get(
                'threebot.initialization')
        return self._user_bot_model

    def initialization_token(self, bootstrap_token):
        """
        ```in
        bootstrap_token = "" (S)
        ```
        """

        if bootstrap_token != os.environ.get('BOOTSTRAP_TOKEN'):
            raise PermissionError('Invalid bootstrap token')

        user_settings = self.user_bot_model.get_by_name('user_initialization')
        if not user_settings:
            raise RuntimeError('Initialization token is not set')
        return user_settings[0].token
