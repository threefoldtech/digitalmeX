from Jumpscale import j

from .ZOSNodes import ZOSNodes


class ZOSCmdFactory(j.application.JSFactoryConfigsBaseClass):

    __jslocation__ = "j.kosmos.zos"

    _CHILDCLASSES = [ZOSNodes]

    def test(self):
        """

        js_shell 'j.kosmos.zos.test()'

        :return:
        """
        # node = self.zosnodes.mynode

        j.shell()
