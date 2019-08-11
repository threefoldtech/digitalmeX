
 from Jumpscale import j

 class Package(j.application.ThreeBotPackageBase):

     def prepare(self):
         """
         is called at install time
         :return:
         """
         pass

     def start(self):
         """
         called when the 3bot starts
         :return:
         """
         pass

     def stop(self):
         """
         called when the 3bot stops
         :return:
         """
         pass

     def delete(self):
         """
         called when the package is no longer needed and will be removed from the threebot
         :return:
         """
         pass
