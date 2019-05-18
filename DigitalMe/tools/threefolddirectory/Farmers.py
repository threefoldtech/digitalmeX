from Jumpscale import j


class Farmer(j.application.JSBaseConfigClass):
    """
    one farmer instance
    """

    _SCHEMATEXT = """
        @url = threefold.grid.farmer
        name* = ""
        description = ""
        error = ""
        iyo_org* = ""
        wallets = (LS)
        emailaddr = (LS)
        mobile = (LS)
        """

    def _init(self):
        pass


class Farmers(j.application.JSBaseConfigsClass):
    """
    ...
    """

    _CHILDCLASS = Farmer
