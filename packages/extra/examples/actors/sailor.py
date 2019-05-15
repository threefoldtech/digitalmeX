from Jumpscale import j
import sys

JSBASE = j.application.JSBaseClass


class sailor(JSBASE):
    """
    """

    def sail(self, msg):
        print("sail:%s" % msg)
        return msg

    def rain(self):
        print("rain")
        return None
