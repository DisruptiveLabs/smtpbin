import asyncore
import errno
import re

from smtpbin.http.exceptions import HTTPError
from smtpbin.http.handlers.api.inbox import APIInboxHandler
from smtpbin.http.handlers.api.inboxes import APIInboxesHandler
from smtpbin.http.handlers.api.index import APIIndexHandler
from smtpbin.http.handlers.api.messages import APIMessagesHandler
from smtpbin.http.handlers.api.message import APIMessageHandler
from smtpbin.http.handlers.error import ErrorHandler
from smtpbin.http.handlers.index import IndexHandler
from smtpbin.http.handlers.static import StaticHandler
from smtpbin.http.request import HTTPRequest


class HTTPRouter(asyncore.dispatcher):
    error = ErrorHandler

    # Note: the map is order dependent. Place catch-alls last
    map = {
        re.compile(r'^/$'): IndexHandler,

        re.compile('^/api/?$'): APIIndexHandler,
        re.compile('^/api/inbox/?$'): APIInboxesHandler,
        re.compile('^/api/inbox/(?P<inbox_name>[\w\.]+)/?$'): APIInboxHandler,
        re.compile('^/api/inbox/(?P<inbox_name>[\w\.]+)/messages/?$'): APIMessagesHandler,
        re.compile('^/api/inbox/(?P<inbox_name>[\w\.]+)/messages/(?P<message_id>\d+)/?$'): APIMessageHandler,

        # Catch-all routes
        re.compile(r'^/.*\.(png|css|jsx?)$'): StaticHandler,
    }

    def __init__(self, client, addr, server):
        asyncore.dispatcher.__init__(self, client)
        self.database = server.database

    def read_request(self):
        reqdata = b''
        sent_100 = False

        while True:
            try:
                data = self.recv(1024)
                if data:
                    reqdata += data
                if not data or len(data) < 1024:
                    if not sent_100 and b'100-continue' in reqdata:
                        sent_100 = True
                        self.send(b'HTTP/1.1 100 Continue\r\n')
                    else:
                        break
            except IOError as ioerror:
                if ioerror.errno == errno.EAGAIN:
                    pass
                elif ioerror.errno == errno.EWOULDBLOCK:
                    pass

        return reqdata

    def handle_read(self):
        # Get the whole request

        data = self.read_request()

        req = HTTPRequest(data)

        print(req.command, req.path)

        try:
            for path, handler in self.map.items():
                matches = path.match(req.path)
                if matches:
                    handler(self).dispatch(req, **matches.groupdict())
                    break
            else:
                print("Cant find route for {}" .format(req.path))
                self.error(self).dispatch(req, HTTPError(404))
        except Exception as e:
            self.error(self).dispatch(req, e)

        self.close()
