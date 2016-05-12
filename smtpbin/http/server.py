# See http://code.activestate.com/recipes/259148-simple-http-server-based-on-asyncoreasynchat/ for a different approach. Might make 100-continue easier...

import asyncore
import socket

from smtpbin.backend.database import DataBase
from smtpbin.http.router import HTTPRouter


class HTTPServer(asyncore.dispatcher):
    def __init__(self, addr):
        self.addr = addr
        self.database = DataBase()

        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)

        self.set_reuse_addr()
        self.bind(self.addr)
        self.listen(5)
        print("Listening for HTTP on {0}:{1}".format(*addr))

    def handle_accept(self):
        (client, addr) = self.accept()
        HTTPRouter(client, addr, self)


if __name__ == '__main__':
    server = HTTPServer(('', 8080))
    asyncore.loop()
