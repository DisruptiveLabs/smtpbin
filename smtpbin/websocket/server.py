import asyncore
import logging
import socket
import sys

from smtpbin.websocket.handler import WebSocket

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(logging.Formatter())
log.addHandler(handler)


class WebSocketServer(asyncore.dispatcher):
    def __init__(self, addr, database):
        asyncore.dispatcher.__init__(self)

        self.addr, self.port = addr
        self.database = database
        database.websocketserver = self

        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketbind = addr[0]
        self.set_reuse_addr()
        self.bind(addr)
        self.connections = {}

        self.listen(5)
        log.info("Listening for WebSocket on {0}:{1}".format(*addr))

    def handle_accept(self):
        (client, addr) = self.accept()
        self.connections[client.fileno()] = WebSocket(client, addr, self)

    def broadcast(self, message):
        for _, websocket in self.connections.items():
            websocket.send(message)
