import asyncore
import os

from .http.server import HTTPServer
from .smtp.server import SMTPBinServer

LISTEN_ADDR = os.environ.get('LISTEN_ADDR', '0.0.0.0')
HTTP_PORT = int(os.environ.get('HTTP_PORT', '8000'))
SMTP_PORT = int(os.environ.get('SMTP_PORT', '25000'))

httpd = HTTPServer((LISTEN_ADDR, HTTP_PORT))
smtpd = SMTPBinServer((LISTEN_ADDR, SMTP_PORT))

try:
    asyncore.loop(timeout=2)
except KeyboardInterrupt:
    pass

