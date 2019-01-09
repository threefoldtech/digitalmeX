from Jumpscale import j

from .ZOSNode import ZOSNode



class ZOSCmdFactory(j.application.JSFactoryBaseClass):

    __jslocation__ = "j.kosmos.zos"

    ZOSNode = ZOSNode

    def _init(self):
        self.zosnodes={}

    def get(self,name,**args):
        if name not in self.zosnodes:
            self.zosnodes[name]=ZOSNode(name=name)
            self.zosnodes[name].data_update(**args)
        return self.zosnodes[name]


    def test(self):
        """

        :return:
        """
        pass

        #TODO: deploy zos in virtualbox
        #...
