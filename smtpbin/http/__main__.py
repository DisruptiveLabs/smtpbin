import asyncore

from .server import HTTPServer

httpd = HTTPServer(('0.0.0.0', 8000))
asyncore.loop()
