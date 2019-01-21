from Jumpscale import j

from .ZOSNodes import ZOSNodes



class ZOSCmdFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.kosmos.zos"

    _CHILDCLASSES = [ZOSNodes]


    def test(self):
        """

        js_shell 'j.kosmos.zos.test()'

        :return:
        """
        pass

