import asyncore

from .server import SMTPBinServer

smtpd = SMTPBinServer(('0.0.0.0', 25000))
asyncore.loop()
