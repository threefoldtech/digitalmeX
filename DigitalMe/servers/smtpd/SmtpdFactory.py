from Jumpscale import j

from .SmtpdServer import SmtpdServer

JSConfigs = j.application.JSBaseConfigsClass


class SmtpdFactory(JSConfigs):

    __jslocation__ = "j.servers.smtpd"
    _CHILDCLASS = SmtpdServer

    def _init(self):
        self._logger_enable()

    def __init__(self):
        JSConfigs.__init__(self)
        self._default = None


    @property
    def default(self):
        if not self._default:
            self._default = self.get("default")
        return self._default


    def test(self):
        x = j.servers.smtpd.get()
        x.start(background=True)
        from smtplib import SMTP
        with SMTP("localhost", 6662) as smtp:
            print(smtp.noop())

        import smtplib
        server = smtplib.SMTP('smtp.gmail.com', 6662)

        # Next, log in to the server
        server.login("localhost", "password")

        # Send the mail
        msg = "Hello!" # The /n separates the message from the headers
        server.sendmail("you@gmail.com", "target@example.com", msg)
