import asyncore
import re

from smtpbin.http.exceptions import HTTPError
from smtpbin.http.handlers.api.messages import MessagesHandler
from smtpbin.http.handlers.error import ErrorHandler
from smtpbin.http.handlers.index import IndexHandler
from smtpbin.http.request import HTTPRequest


class HTTPRouter(asyncore.dispatcher):
    error = ErrorHandler

    # Note: the map is order dependent. Place catch-alls last
    map = {
        re.compile(r'^/$'): IndexHandler,
        re.compile(r'^/api/messages'): MessagesHandler,
    }

    def __init__(self, client, addr, server):
        asyncore.dispatcher.__init__(self, client)
        self.db = server.db

    def handle_read(self):
        # Get the whole request
        data = self.recv(1024)
        req = HTTPRequest(data)

        print(req.command, req.path)

        try:
            for path, handler in self.map.items():
                if path.match(req.path):
                    handler(self).dispatch(req)
                    break
            else:
                self.error(self).dispatch(req, HTTPError(404))
        except Exception as e:
            self.error(self).dispatch(req, e)

        self.close()
