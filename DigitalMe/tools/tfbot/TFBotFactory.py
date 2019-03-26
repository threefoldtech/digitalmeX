from Jumpscale import j
from DigitalMe.tools.builder.ZOSContainer import ZOSContainer
import re
from io import StringIO
import os
import locale

JSBASE = j.application.JSBaseClass

from .TFBot import TFBot


class TFBotFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.tools.tfbot"
        JSBASE.__init__(self)
        self._tbots={}





    def test(self):
        """
        js_shell 'j.tools.tbot.test()'
        """
        bot = self.get()
        print(bot.node)
        j.shell()
