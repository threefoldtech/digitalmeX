from Jumpscale import j


# from Jumpscale.data.bcdb.connectors.webdav.BCDBFSProvider import BCDBFSProvider
JSConfigClient = j.application.JSBaseConfigClass



class SmtpdServer(JSConfigClient):
    _SCHEMATEXT = """
       @url =  jumpscale.servers.smtpd
       name* = "default" (S)
       port = 6662 (I)
       """

    def start(self, background=False, debug=False):

        from .gsmtpd import SMTPServer

        class MailServer(SMTPServer):
            # Do something with the gathered message
            def process_message(self, peer, mailfrom, rcpttos, data):
                inheaders = 1
                lines = data.split('\n')
                print('---------- MESSAGE FOLLOWS ----------')
                for line in lines:
                    # headers first
                    if inheaders and not line:
                        print('X-Peer:', peer[0])
                        inheaders = 0
                    print(line)
                print('------------ END MESSAGE ------------')

        if not background:
            server = MailServer(('0.0.0.0', self.port))
            rack = j.servers.rack.get()
            rack.add(name=self.name, server=server)
            rack.start()