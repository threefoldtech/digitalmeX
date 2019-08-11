from Jumpscale import j

from .ThreeBotPackage import ThreeBotPackage


class ThreeBotPackageFactory(j.application.JSBaseConfigClass):
    """
    deal with 3bot packages

    """

    __jslocation__ = "j.tools.threebotpackage"
    _CHILDCLASS = ThreeBotPackage

    def test(self):
        """
        kosmos -p 'j.tools.threebotpackage.test()'
        """
        wg = self.get(name="test", giturl = )


        j.shell()
