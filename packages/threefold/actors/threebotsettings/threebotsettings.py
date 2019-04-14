from Jumpscale import j
import onetimepass

JSBASE = j.application.JSBaseClass

class threebotsettings(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)

        j.tools.threefold_threebot.zdb = j.clients.zdb.testdb_server_start_client_admin_get(reset=False, secret="123456")
        self._bcdb = j.data.bcdb.bcdb_instances["default"]
        self._threebotsettings_model = None

    @property
    def threebotsettings_model(self):
        if not self._threebotsettings_model:
            self._threebotsettings_model = self._bcdb.model_get('threefold.grid.threebotsettings')
        return self._threebotsettings_model

    def get_otp(self, doubleName):
        bot_model = None
        threebots = self.threebotsettings_model.get_all()
        for bot in threebots:
            if bot.doubleName == doubleName:
                bot_model = bot
                break

        if bot_model:
            if bot_model.totp_secret == "":
                secret = j.data.idgenerator.generateXCharID(8)
                bot_model.totp_secret = secret
                self.threebotsettings_model.set(bot_model)
            totp = onetimepass.get_totp(bot_model.totp_secret)
            return totp

        return False

    def get_threebotsettings(self, doubleName, schema_out):
        """
        ```in
        doubleName = (S)
        ```

        ```out
        !threefold.grid.threebotsettings
        ```
        """
        out = schema_out.new()
        threebots = self.threebotsettings_model.get_all()
        for bot in threebots:
            if bot.doubleName == doubleName:
                out.res = bot
                break
        # TODO: make sure u don't return the totp here
        return out

    def update_threebotsettings(self, doubleName, totp, firstName, lastName, email, addressStreet, addressNumber, addressZipcode, addressCity, addressCountry, telephone):
        """
        ```in
        doubleName = (S)
        ```
        """
        bot_model = None
        threebots = self.threebotsettings_model.get_all()
        for bot in threebots:
            if bot.doubleName == doubleName:
                bot_model = bot
                break
        
        if bot_model and onetimepass.valid_totp(totp, bot_model.totp_secret):
            bot_model.firstName = firstName
            bot_model.lastName = lastName
            bot_model.email = email
            bot_model.addressStreet = addressStreet
            bot_model.addressNumber = addressNumber
            bot_model.addressZipcode = addressZipcode
            bot_model.addressCity = addressCity
            bot_model.addressCountry = addressCountry
            bot_model.telephone = telephone

            self.threebotsettings_model.set(bot_model)
            return True

        return False
